from django.db import models

### 데이터베이스 생성 코드 부분 ###
class Device(models.Model):
    STATUS_ONLINE = "online"
    STATUS_WARNING = "warning"
    STATUS_OFFLINE = "offline"

    STATUS_CHOICES = [
        (STATUS_ONLINE, "online"),
        (STATUS_WARNING, "warning"),
        (STATUS_OFFLINE, "offline"),
    ]

    id = models.BigAutoField(primary_key=True)
    device_number = models.CharField(max_length=50, unique=True)
    device_mac = models.CharField(max_length=17, unique=True)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_ONLINE,
    )
    last_ping = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_number} ({self.device_mac})"