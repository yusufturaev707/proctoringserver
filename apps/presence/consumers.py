"""
PresenceConsumer — WebSocket orqali foydalanuvchi online/offline holatini boshqarish.

Protokol:
  ws://host/ws/presence/?token=<JWT_ACCESS_TOKEN>&mac_address=<MAC>&local_ip=<IP>&zone_id=<ID>

Connect:
  - JWT token tekshiriladi
  - PresenceConnection yaratiladi (is_online=True)
  - Admin dashboard guruhiga xabar yuboriladi

Disconnect:
  - PresenceConnection -> is_online=False, disconnected_at=now
  - Admin dashboard guruhiga xabar yuboriladi
"""
import ipaddress
import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)

DASHBOARD_GROUP = "presence_dashboard"
ADMIN_MAC_PREFIX = "admin-"  # Admin dashboard ulanishlari shu prefix bilan keladi


def _sanitize_ip(raw):
    """IP stringni tekshirish. Noto'g'ri bo'lsa None qaytaradi."""
    if not raw:
        return None
    try:
        return str(ipaddress.ip_address(raw.strip()))
    except (ValueError, AttributeError):
        return None


class PresenceConsumer(AsyncJsonWebsocketConsumer):
    """Foydalanuvchi ulanish holatini kuzatuvchi WebSocket consumer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.mac_address = None
        self.public_ip = None
        self.local_ip = None
        self.zone_id = None
        self.connection_id = None
        self.is_admin_viewer = False  # Admin dashboard dan ulanganmi

    # ──────────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────────

    async def connect(self):
        try:
            query_params = parse_qs(self.scope["query_string"].decode())

            # 1. Token validatsiya
            token_list = query_params.get("token", [])
            if not token_list:
                logger.warning("[Presence] Token yo'q — reject")
                await self.close(code=4001)
                return

            self.user = await self._authenticate(token_list[0])
            if not self.user:
                logger.warning("[Presence] Token yaroqsiz — reject")
                await self.close(code=4001)
                return

            # 2. MAC address va IP larni olish
            mac_list = query_params.get("mac_address", [])
            self.mac_address = mac_list[0] if mac_list else "00:00:00:00:00:00"

            local_ip_list = query_params.get("local_ip", [])
            self.local_ip = _sanitize_ip(local_ip_list[0] if local_ip_list else None)

            zone_id_list = query_params.get("zone_id", [])
            self.zone_id = int(zone_id_list[0]) if zone_id_list and zone_id_list[0].isdigit() else None

            # Public IP ni request headerdan olish
            headers = dict(self.scope.get("headers", []))
            x_forwarded = headers.get(b"x-forwarded-for", b"").decode()
            if x_forwarded:
                self.public_ip = _sanitize_ip(x_forwarded.split(",")[0])
            else:
                peer = self.scope.get("client")
                self.public_ip = _sanitize_ip(peer[0] if peer else None)

            # Admin dashboard ulanishini aniqlash
            self.is_admin_viewer = self.mac_address.startswith(ADMIN_MAC_PREFIX)

            # 3. Ulanishni qabul qilish
            await self.accept()

            # 4. Faqat desktop clientlar uchun DB ga yozish
            if not self.is_admin_viewer:
                self.connection_id = await self._register_connection()

            # 5. Dashboard guruhiga qo'shilish va yangilash
            await self.channel_layer.group_add(DASHBOARD_GROUP, self.channel_name)
            await self._broadcast_dashboard_update()

            logger.info(
                f"[Presence] Connected: {self.user.username} | "
                f"MAC: {self.mac_address} | IP: {self.public_ip} | "
                f"ConnID: {self.connection_id} | Admin: {self.is_admin_viewer}"
            )
        except Exception as e:
            logger.exception(f"[Presence] Connect xatolik: {e}")
            await self.close(code=4500)

    async def disconnect(self, close_code):
        try:
            if self.connection_id:
                await self._mark_disconnected()
                await self._broadcast_dashboard_update()

            await self.channel_layer.group_discard(DASHBOARD_GROUP, self.channel_name)
        except Exception as e:
            logger.exception(f"[Presence] Disconnect xatolik: {e}")

        username = self.user.username if self.user else "unknown"
        logger.info(f"[Presence] Disconnected: {username} | MAC: {self.mac_address}")

    async def receive_json(self, content, **kwargs):
        """Client dan kelgan xabarlar (ping/pong uchun)."""
        msg_type = content.get("type")

        if msg_type == "ping":
            await self.send_json({"type": "pong"})

    # ──────────────────────────────────────────────
    # Dashboard group handler
    # ──────────────────────────────────────────────

    async def presence_update(self, event):
        """Dashboard guruhiga yuborilgan xabarni clientga uzatish."""
        await self.send_json(event["data"])

    # ──────────────────────────────────────────────
    # Authentication
    # ──────────────────────────────────────────────

    @database_sync_to_async
    def _authenticate(self, token_str):
        """JWT access token ni tekshirish va User obyektini qaytarish."""
        try:
            access_token = AccessToken(token_str)
            user_id = access_token["user_id"]

            from apps.users.models import User
            return User.objects.get(id=user_id, is_active=True)
        except Exception as e:
            logger.warning(f"[Presence] Auth xatolik: {e}")
            return None

    # ──────────────────────────────────────────────
    # DB operations
    # ──────────────────────────────────────────────

    @database_sync_to_async
    def _register_connection(self):
        """Yangi ulanishni DB ga yozish. Eski ulanishni offline qilish."""
        from apps.presence.models import PresenceConnection

        now = timezone.now()

        # Agar shu user + mac_address bilan eski online connection bo'lsa, offline qilish
        stale_count = PresenceConnection.objects.filter(
            user=self.user,
            mac_address=self.mac_address,
            is_online=True,
        ).update(is_online=False, disconnected_at=now)

        if stale_count:
            logger.info(f"[Presence] {stale_count} ta eski ulanish offline qilindi: "
                        f"{self.user.username} / {self.mac_address}")

        # Agar channel_name bilan eski record bor bo'lsa, tozalash
        PresenceConnection.objects.filter(
            channel_name=self.channel_name,
            is_online=True,
        ).update(is_online=False, disconnected_at=now)

        try:
            conn = PresenceConnection.objects.create(
                user=self.user,
                mac_address=self.mac_address,
                channel_name=self.channel_name,
                is_online=True,
                public_ip=self.public_ip,
                local_ip=self.local_ip,
                zone_id=self.zone_id,
            )
            logger.info(f"[Presence] DB record yaratildi: id={conn.id} | "
                        f"{self.user.username} | {self.mac_address}")
            return conn.id
        except Exception as e:
            logger.exception(f"[Presence] DB yozishda xatolik: {e}")
            return None

    @database_sync_to_async
    def _mark_disconnected(self):
        """Ulanishni offline qilish."""
        from apps.presence.models import PresenceConnection

        PresenceConnection.objects.filter(id=self.connection_id).update(
            is_online=False,
            disconnected_at=timezone.now(),
        )

    # ──────────────────────────────────────────────
    # Broadcasting
    # ──────────────────────────────────────────────

    async def _broadcast_dashboard_update(self):
        """Admin dashboard ga yangilangan statistikani yuborish."""
        stats = await self._get_dashboard_stats()
        await self.channel_layer.group_send(
            DASHBOARD_GROUP,
            {
                "type": "presence.update",
                "data": {
                    "type": "dashboard_update",
                    **stats,
                },
            },
        )

    @database_sync_to_async
    def _get_dashboard_stats(self):
        """Dashboard uchun statistikani hisoblash. Faqat desktop clientlar."""
        from datetime import timedelta

        from django.db.models import Count

        from apps.presence.models import PresenceConnection

        # Admin dashboard ulanishlarini chiqarib tashlash
        online_qs = PresenceConnection.objects.filter(
            is_online=True,
        ).exclude(
            mac_address__startswith=ADMIN_MAC_PREFIX,
        )

        total_online = online_qs.count()
        unique_users_online = online_qs.values("user").distinct().count()
        unique_pcs_online = online_qs.values("mac_address").distinct().count()

        # Har bir user uchun online PClar
        users_detail = list(
            online_qs.values(
                "user__id",
                "user__username",
                "user__first_name",
                "user__last_name",
                "user__region__id",
                "user__region__name",
                "user__role__id",
                "user__role__name",
            )
            .annotate(online_pcs=Count("mac_address", distinct=True))
            .order_by("user__username")
        )

        # Har bir user uchun MAC, IP, zone ro'yxati
        for user_stat in users_detail:
            connections = list(
                online_qs.filter(user__id=user_stat["user__id"])
                .values("mac_address", "public_ip", "local_ip", "zone__id", "zone__name")
                .distinct()
            )
            user_stat["mac_list"] = list({c["mac_address"] for c in connections})
            user_stat["ip_list"] = [
                {
                    "mac": c["mac_address"],
                    "public_ip": c["public_ip"] or "",
                    "local_ip": c["local_ip"] or "",
                }
                for c in connections
            ]
            zones = {c["zone__id"]: c["zone__name"] for c in connections if c["zone__id"]}
            user_stat["zone_ids"] = list(zones.keys())
            user_stat["zone_names"] = list(zones.values())

        return {
            "total_online_connections": total_online,
            "unique_users_online": unique_users_online,
            "unique_pcs_online": unique_pcs_online,
            "users": users_detail,
        }
