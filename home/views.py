from django.shortcuts import render

def index(request):
    context = {
        'segment': 'index'
    }
    return render(request, 'home/index.html', context)

def tables(request):
    context = {
        'segment': 'tables'
    }
    return render(request, 'home/tables.html', context)

def map(request):
    context = {
        'segment': 'map'
    }
    return render(request, 'home/map.html', context)