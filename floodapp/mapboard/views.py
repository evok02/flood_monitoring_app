
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import WaterLevel, Station, Region, EmergencyReport, Station, Measurement
from .decorators import allowed_users, unauthenticated_user
import json
from .models import Event
from .form import EventForm, DeleteForm, EventUpdateForm, EventSelectForm
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


#@allowed_users(allowed_roles=['admin'])
def task_scheduling_page(request):
    events = Event.objects.all()
    return render(request, 'schedule.html', {'events': events})

def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            return redirect('http://127.0.0.1:8000/map/schedule/')
            return JsonResponse({
                'id': event.id,
                'title': event.title,
                'start': event.start_time,
                'end': event.end_time,
                'description': event.description,
            })
    else:
        form = EventForm()
    return render(request, 'add_event.html', {'form': form})


def event_list(request):
    events = Event.objects.all()
    data = [{
        'id': event.id,
        'title': event.title,
        'start': event.start_time,
        'end': event.end_time,
    } for event in events]
    return JsonResponse(data, safe=False)
    

def delete_event(request):
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            event_id = form.cleaned_data['event_id']
            try:
                event = Event.objects.get(id=event_id)
                event.delete()
                return redirect('http://127.0.0.1:8000/map/schedule/')
            except Event.DoesNotExist:
                return JsonResponse({'error': 'Event not found'}, status=404)
        return JsonResponse({'error': 'Invalid form data'}, status=400)
    else:
        form = DeleteForm()
    return render(request, 'delete_event.html', {'form': form})



def update_event(request):
    if request.method == 'POST':
        if 'select_event' in request.POST:
            select_form = EventSelectForm(request.POST)
            if select_form.is_valid():
                title = select_form.cleaned_data['title']
                try:
                    event = Event.objects.get(title=title)
                except Event.DoesNotExist:
                    return JsonResponse({'error': 'Event not found'}, status=404)
                update_form = EventUpdateForm(instance=event)
                return render(request, 'update_event.html', {'update_form': update_form, 'select_form': select_form, 'event': event})
        

        elif 'update_event' in request.POST:
            event = Event.objects.get(id=request.POST.get('event_id')) 
            update_form = EventUpdateForm(request.POST, instance=event)
            if update_form.is_valid():
                update_form.save()
                return redirect('http://127.0.0.1:8000/map/schedule/')
            else:
                return JsonResponse({'error': 'Invalid data submitted'}, status=400)
    else:
        select_form = EventSelectForm()
        update_form = None

    return render(request, 'update_event.html', {'select_form': select_form, 'update_form': update_form})
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
