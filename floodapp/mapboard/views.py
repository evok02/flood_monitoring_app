from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import WaterLevel, Station, Region, EmergencyReport, Station, Measurement
from .decorators import allowed_users, unauthenticated_user
import json
import logging

logger = logging.getLogger('flood_app')

def water_levels_api(request):
    logger.info('Fetching water levels from database.')
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
    logger.info('Fetched water levels.')
    return render(request, 'mapboard.html')

def waterlevel_map(request):
    logger.info('Rendering water level map.')
    return render(request, "waterlevel_map.html")

@allowed_users(allowed_roles=['admin'])
def admin_only_page(request):
    logger.info(f'Admin page accessed by user {request.user.username}')
    return render(request, 'admin_only_page.html')



def water_level_history(request, region_id):
    logger.info(f'Fetching water level history for region {region_id}')
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
        logger.info(f'Fetched water level history for region {region_id}')
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        logger.info(f'Error fetching water level history for region {region_id}')
        return JsonResponse({'success': False, 'error': str(e)})


def report_emergency_view(request):
    logger.info('Rendering emergency report page')
    regions = Region.objects.all()
    return render(request, 'report_emergency.html', {'regions': regions})

def historical_data_view(request):
    station_id = request.GET.get('hzbnr')
    if not station_id:
        logger.info('station_id is empty, but required')
        return render(request, 'error.html', {'message': 'Station ID is required.'})

    # Fetch station metadata
    station = get_object_or_404(Station, hzbnr=station_id)
    logger.info(f'Fetched station metadata for station {station_id}')

    # Fetch measurements
    measurements = Measurement.objects.filter(station_id=station.id).order_by('timestamp')
    logger.info(f'Fetched measurements for station {station_id}')

    context = {
        'station': station,
        'measurements': measurements,
    }
    return render(request, 'historical_data.html', context)