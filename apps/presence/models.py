from django.db import models
from core.models.base import BaseModel


class PresenceConnection(BaseModel):
    """
    Har bir WebSocket ulanishni saqlash.
    Bitta username bir nechta kompyuterdan (mac_address) ulanishi mumkin.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='presence_connections',
    )
    mac_address = models.CharField(max_length=32)
    channel_name = models.CharField(max_length=255, unique=True)
    is_online = models.BooleanField(default=True, db_index=True)
    public_ip = models.GenericIPAddressField(null=True, blank=True)
    local_ip = models.GenericIPAddressField(null=True, blank=True)
    zone = models.ForeignKey(
        'regions.Zone',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='presence_connections',
    )
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'presence_connection'
        verbose_name = 'Ulanish'
        verbose_name_plural = 'Ulanishlar'
        ordering = ['-connected_at']
        indexes = [
            models.Index(fields=['user', 'is_online']),
            models.Index(fields=['mac_address', 'is_online']),
        ]

    def __str__(self):
        status = 'Online' if self.is_online else 'Offline'
        return f"{self.user.username} — {self.mac_address} [{status}]"
