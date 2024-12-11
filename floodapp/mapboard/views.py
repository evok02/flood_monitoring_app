from django.shortcuts import render
from django.http import JsonResponse
from .models import WaterLevel, EmergencyReport, Region
from django.http import HttpResponseRedirect
from django.urls import reverse

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

def water_level_history(request, region_id):
    try:
        # Query water levels for the specific region
        # Order it by -timestamp because we need to show the most recent updates at the top
        water_levels = WaterLevel.objects.filter(region_id=region_id).order_by('-timestamp')
        # JSON response:
        data = [
            {
                "water_level": wl.water_level,
                "risk_level": wl.risk_level,
                "timestamp": wl.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for wl in water_levels
        ]
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Report an emergency
def report_emergency(request):
    if request.method == 'POST':
        region_id = request.POST.get('region')
        description = request.POST.get('description')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        urgency_level = request.POST.get('urgency_level')

        try:
            region = Region.objects.get(id=region_id)
            EmergencyReport.objects.create(
                region=region,
                description=description,
                location=location,
                latitude=latitude,
                longitude=longitude,
                urgency_level=urgency_level,
            )
            # Redirect to the map after successful submission
            return HttpResponseRedirect(reverse('map'))
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        regions = Region.objects.all()
        return render(request, 'report_emergency.html', {'regions': regions})

# Fetch emergencies for map
def fetch_emergencies_view(request):
    emergencies = EmergencyReport.objects.select_related('region').all()
    data = [
        {
            "region": emergency.region.name,
            "description": emergency.description,
            "latitude": emergency.region.latitude,
            "longitude": emergency.region.longitude,
            "location": emergency.location,
            "urgency_level": emergency.urgency_level,
        }
        for emergency in emergencies
    ]
    return JsonResponse(data, safe=False)