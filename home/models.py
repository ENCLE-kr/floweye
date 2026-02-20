from django.db import models

### 데이터베이스 생성 코드 부분 ###
class Device(models.Model):
    # id 필드는 Django가 기본적으로 PK로 생성합니다 (integer, PK).
    
    device_number = models.CharField(max_length=50, unique=True, verbose_name="기기 번호")
    device_mac = models.CharField(
        max_length=17, 
        unique=True, 
        db_index=True, 
        verbose_name="디바이스 MAC 주소"
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    
    # 위도/경도는 DecimalField가 정확도 측면에서 유리합니다.
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    status = models.CharField(max_length=20, default="active")
    last_ping = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "home_device"

    def __str__(self):
        return f"{self.device_number} ({self.device_mac})"


class DeviceLog(models.Model):
    # 다이어그램에 따라 home_device.id를 참조하는 FK 설정
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="logs",
        db_column="device_id"  # DB 컬럼명을 다이어그램과 일치시킴
    )
    # 인원 집계 시 성능을 위해 db_index 추가
    src_mac = models.CharField(max_length=17, db_index=True, verbose_name="소스 MAC 주소")
    # 시간 범위 조회가 잦으므로 인덱스 추가
    time = models.DateTimeField(db_index=True, verbose_name="로그 시간")
    rssi = models.IntegerField()

    class Meta:
        db_table = "home_devicelog"

class DeviceStatus(models.Model):
    # 다이어그램에 따라 home_device.id를 참조하는 FK 설정
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="statuses",
        db_column="device_id"
    )
    target_date = models.DateField(db_index=True)
    target_hour = models.IntegerField()
    # 5분 단위 슬롯 (0, 5, 10, ..., 55)
    target_minute = models.IntegerField(default=0, db_index=True)
    
    current_stay_count = models.IntegerField(default=0)
    current_density = models.DecimalField(max_digits=7, decimal_places=2, default=0.0)
    
    today_visitor_count = models.IntegerField(default=0)
    period_visitor_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "home_device_status"
        # 시간대별(5분 단위), 기기별 유니크 제약 추가
        constraints = [
            models.UniqueConstraint(
                fields=['device', 'target_date', 'target_hour', 'target_minute'],
                name='unique_device_time_slot'
            )
        ]

    def __str__(self):
        return f"{self.device.device_mac} - {self.target_date} {self.target_hour}h {self.target_minute}m"