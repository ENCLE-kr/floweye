from django.shortcuts import render, redirect

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
    context = {
        'segment': 'devices',
        'page_title': 'Devices'
    }
    return render(request, 'home/devices.html', context)