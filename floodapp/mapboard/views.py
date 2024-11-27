from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.from django.http import JsonResponse
from .models import WaterLevel, Station
import json 
def mapboard_view(request):
    stations = Station.objects.all()
    data = [
        {"x": float(station.x), "y": float(station.y), "hzbnr01": station.hzbnr01}
        for station in stations
    ]
    return render(request, 'mapboard.html', {'stations_data': json.dumps(data)})


