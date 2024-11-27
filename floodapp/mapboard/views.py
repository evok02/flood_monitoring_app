from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.from django.http import JsonResponse
from .models import WaterLevel, Station
import json
# def water_levels_api(request):
#     levels = WaterLevel.objects.select_related('region').all()
#     data = [
#         {
#             "region": wl.region.name,
#             "latitude": wl.region.latitude,
#             "longitude": wl.region.longitude,
#             "water_level": wl.water_level,
#             "risk_level": wl.risk_level
#         }
#         for wl in levels
#     ]
#     return render(request, 'mapboard.html', {'data': data})


def mapboard_view(request):
    stations = Station.objects.all()
    data = [
        {"x": float(station.x), "y": float(station.y), "hzbnr01": station.hzbnr01}
        for station in stations
    ]
    return render(request, 'mapboard.html', {'stations_data': json.dumps(data)})


