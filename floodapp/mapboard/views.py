from django.shortcuts import render
from django.http import JsonResponse
from .models import WaterLevel

def water_levels_api(request):
    levels = WaterLevel.objects.select_related('region').all()
    data = [
        {
            "region": wl.region.name,
            "latitude": wl.region.latitude,
            "longitude": wl.region.longitude,
            "water_level": wl.water_level,
            "risk_level": wl.risk_level
        }
        for wl in levels
    ]
    return render(request, 'mapboard.html')

def admin_only_page(request):
    return render(request, 'admin_only_page.html')
