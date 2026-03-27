import logging
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.presence.consumers import ADMIN_MAC_PREFIX
from apps.presence.models import PresenceConnection
from apps.regions.models import Region, Zone
from apps.users.models import Role

logger = logging.getLogger(__name__)


@staff_member_required
def presence_dashboard_view(request):
    """Admin panel uchun online monitoring dashboard."""

    # Stale connectionlarni tozalash: 24 soatdan eski "online" recordlar
    stale_cutoff = timezone.now() - timedelta(hours=24)
    stale_cleaned = PresenceConnection.objects.filter(
        is_online=True,
        connected_at__lt=stale_cutoff,
    ).update(is_online=False, disconnected_at=timezone.now())
    if stale_cleaned:
        logger.info(f"[Presence] {stale_cleaned} ta stale connection tozalandi")

    online_qs = PresenceConnection.objects.filter(
        is_online=True,
    ).exclude(
        mac_address__startswith=ADMIN_MAC_PREFIX,
    )

    total_online_connections = online_qs.count()
    unique_users_online = online_qs.values("user").distinct().count()
    unique_pcs_online = online_qs.values("mac_address").distinct().count()

    users_stats = list(
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

    for user_stat in users_stats:
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

    # Filtr uchun
    regions = list(Region.objects.values("id", "name").order_by("name"))
    zones = list(Zone.objects.values("id", "name", "region_id").order_by("name"))
    roles = list(Role.objects.values("id", "name").order_by("name"))

    admin_token = ""
    try:
        token = AccessToken.for_user(request.user)
        admin_token = str(token)
    except Exception:
        pass

    context = {
        "total_online_connections": total_online_connections,
        "unique_users_online": unique_users_online,
        "unique_pcs_online": unique_pcs_online,
        "users": users_stats,
        "regions": regions,
        "zones": zones,
        "roles": roles,
        "now": timezone.now().strftime("%H:%M:%S"),
        "admin_token": admin_token,
    }

    return render(request, "admin/presence/dashboard.html", context)
