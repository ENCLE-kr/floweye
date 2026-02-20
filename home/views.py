import json
from datetime import date, datetime
from django.db.models import Avg, Max, Sum
from django.shortcuts import render, redirect

from .models import Device, DeviceStatus

def index(request):
    return redirect('dashboard')

def _density_level(density):
    """밀집도 수치 → 높음/보통/낮음"""
    if density is None:
        return None
    v = float(density)
    if v >= 0.8:
        return ("높음", "text-rose-400")
    if v >= 0.4:
        return ("보통", "text-amber-400")
    return ("낮음", "text-emerald-400")


def dashboard(request):
    devices = Device.objects.all().order_by("-id")
    date_str = request.GET.get("date")
    display_date = date_str or date.today().isoformat()
    try:
        target_date = date.fromisoformat(display_date)
    except ValueError:
        target_date = date.today()

    context = {
        'segment': 'dashboard',
        'page_title': 'Dashboard',
        'devices': devices,
        'date': display_date,
        'stats': None,
        'chart_occupancy': None,
        'chart_density': None,
        'chart_today_visit': None,
    }

    # 디바이스별 해당일 최신 상태 (디바이스 정보 테이블용)
    status_qs = DeviceStatus.objects.filter(target_date=target_date)
    if target_date == date.today():
        status_qs = status_qs.filter(target_hour__lt=datetime.now().hour)
    latest_by_device = {}
    for row in status_qs.order_by("device_id", "-target_hour").iterator():
        if row.device_id not in latest_by_device:
            latest_by_device[row.device_id] = row

    devices_with_status = []
    for device in devices:
        st = latest_by_device.get(device.id)
        if st is not None:
            level_label, level_class = _density_level(st.current_density) or ("—", "text-slate-500")
            devices_with_status.append({
                "device": device,
                "current_stay_count": st.current_stay_count,
                "current_density": float(st.current_density) if st.current_density is not None else None,
                "density_level_label": level_label,
                "density_level_class": level_class,
                "status_updated_at": st.updated_at,
            })
        else:
            devices_with_status.append({
                "device": device,
                "current_stay_count": None,
                "current_density": None,
                "density_level_label": "—",
                "density_level_class": "text-slate-500",
                "status_updated_at": None,
            })
    context["devices_with_status"] = devices_with_status

    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            target_date = None
        if target_date:
            qs = DeviceStatus.objects.filter(target_date=target_date)
            # 당일 선택 시 현재 시각 이전 데이터만 (예: 14:06 → 14시 미만, 0~13시만)
            if target_date == date.today():
                current_hour = datetime.now().hour
                qs = qs.filter(target_hour__lt=current_hour)
            if qs.exists():
                # 해당일 마지막 시간 슬롯 기준 집계
                last_slot = qs.order_by("-target_hour").first()
                last_qs = qs.filter(target_hour=last_slot.target_hour)
                stay_sum = last_qs.aggregate(s=Sum("current_stay_count"))["s"] or 0
                density_avg = last_qs.aggregate(a=Avg("current_density"))["a"] or 0

                # 해당일 오늘 누적 방문: 디바이스별 max(today_visitor_count) 합
                day_end = qs.values("device").annotate(mx=Max("today_visitor_count"))
                today_visit = sum(d["mx"] or 0 for d in day_end)
                period_visit = today_visit  # 단일일 조회 시 기간 누적 = 해당일 누적

                context["stats"] = {
                    "current_stay_total": stay_sum,
                    "current_density_avg": round(float(density_avg), 1),
                    "today_visitor_total": today_visit,
                    "period_visitor_total": period_visit,
                }

                # 차트용 시계열: 해당일 시간순
                slots = qs.values("target_hour").order_by("target_hour").distinct()
                labels = []
                occ_data = []
                dens_data = []
                today_data = []
                for s in slots:
                    th = s["target_hour"]
                    labels.append(f"{th:02d}시")
                    row_qs = qs.filter(target_hour=th)
                    occ_data.append(
                        row_qs.aggregate(s=Sum("current_stay_count"))["s"] or 0
                    )
                    dens_data.append(
                        round(
                            float(
                                row_qs.aggregate(a=Avg("current_density"))["a"] or 0
                            ),
                            1,
                        )
                    )
                    today_data.append(
                        row_qs.aggregate(s=Sum("today_visitor_count"))["s"] or 0
                    )
                context["chart_occupancy"] = {"labels": labels, "data": occ_data}
                context["chart_density"] = {"labels": labels, "data": dens_data}
                context["chart_today_visit"] = {"labels": labels, "data": today_data}
            else:
                # 날짜 선택했으나 데이터 없음 → 0으로 표시
                context["stats"] = {
                    "current_stay_total": 0,
                    "current_density_avg": 0,
                    "today_visitor_total": 0,
                    "period_visitor_total": 0,
                }
                context["chart_occupancy"] = {"labels": [], "data": [0]}
                context["chart_density"] = {"labels": [], "data": [0]}
                context["chart_today_visit"] = {"labels": [], "data": [0]}

    # JS에서 사용할 수 있도록 JSON 문자열로 전달
    for key in ("chart_occupancy", "chart_density", "chart_today_visit"):
        val = context.get(key)
        context[f"{key}_json"] = json.dumps(val, ensure_ascii=False) if val else "null"

    return render(request, 'home/dashboard.html', context)

def map(request):
    context = {
        'segment': 'map',
        'page_title': 'Map'
    }
    return render(request, 'home/map.html', context)

def devices(request):
    devices_data = [
        {
            "device_number": device.device_number,
            "device_mac": device.device_mac,
            "address": device.address,
            "latitude": str(device.latitude),
            "longitude": str(device.longitude),
            "status": device.status,
        }
        for device in Device.objects.all().order_by("-id")
    ]
    context = {
        'segment': 'devices',
        'page_title': 'Devices',
        'devices': devices_data,
    }
    return render(request, 'home/devices.html', context)