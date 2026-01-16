from django.shortcuts import render, redirect

from .models import Device

def index(request):
    return redirect('dashboard')

def dashboard(request):
    context = {
        'segment': 'dashboard',
        'page_title': 'Dashboard'
    }
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
        for device in Device.objects.all().order_by("-created_at")
    ]
    context = {
        'segment': 'devices',
        'page_title': 'Devices',
        'devices': devices_data,
    }
    return render(request, 'home/devices.html', context)