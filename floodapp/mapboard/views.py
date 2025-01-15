
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Max
from .models import WaterLevel, Station, Region, EmergencyReport, Station, Measurement
from .decorators import allowed_users, unauthenticated_user
import json
from django.contrib.auth.decorators import login_required

from .models import Event
from .form import EventForm, DeleteForm, EventUpdateForm, EventSelectForm, GraphParametersForm
import logging
from django.urls import reverse
logger = logging.getLogger('flood_app')
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import io
import urllib, base64
import os



@login_required
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

@login_required
@allowed_users(allowed_roles=['admin'])
def task_scheduling_page(request):
    events = Event.objects.all()
    return render(request, 'schedule.html', {'events': events})

@allowed_users(allowed_roles=['admin'])
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

@allowed_users(allowed_roles=['admin'])
def event_list(request):
    events = Event.objects.all()
    data = [{
        'id': event.id,
        'title': event.title,
        'start': event.start_time,
        'end': event.end_time,
    } for event in events]
    return JsonResponse(data, safe=False)
    
@allowed_users(allowed_roles=['admin'])
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


@allowed_users(allowed_roles=['admin'])
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


def historical_graph_view(request):
    if request.method == 'POST':
        form = GraphParametersForm(request.POST)
        if form.is_valid():
            locations = []
            if form.cleaned_data['location']:
                locations.append(form.cleaned_data['location'])
            
            for key in request.POST.keys():
                if key.startswith('location-') and request.POST[key].strip():
                    locations.append(request.POST[key].strip())
            
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            box_plot_uris = []

            if len(locations) == 2:
                location1, location2 = locations

                max_agg1 = Station.objects.filter(messstelle=location1).values('id').aggregate(max_num=Max('id'))
                st_id1 = max_agg1.get('max_num', 1)
                data1 = Measurement.objects.filter(timestamp__date__range=(start_date, end_date), station_id=st_id1).values('timestamp', 'wert')
                wert1 = list(map(lambda d: d['wert'], data1))
                dates1 = list(map(lambda d: d['timestamp'], data1))

                max_agg2 = Station.objects.filter(messstelle=location2).values('id').aggregate(max_num=Max('id'))
                st_id2 = max_agg2.get('max_num', 1)
                data2 = Measurement.objects.filter(timestamp__date__range=(start_date, end_date), station_id=st_id2).values('timestamp', 'wert')
                wert2 = list(map(lambda d: d['wert'], data2))
                dates2 = list(map(lambda d: d['timestamp'], data2))

                p_bcg = r'.\floodapp\static\images\graph_background1.webp'

                # Line plot
                img = plt.imread(p_bcg)
                fig, ax = plt.subplots()
                ax.imshow(img, extent=[min(dates1 + dates2), max(dates1 + dates2), min(wert1 + wert2), max(wert1 + wert2)], aspect='auto', zorder=0)
                ax.plot(dates1, wert1, 'bo-', label='Location 1', color='cyan', zorder=1)
                ax.plot(dates2, wert2, 'ro-', label='Location 2', color='magenta', zorder=1)
                ax.set_xlabel('Date')
                ax.set_ylabel('Wert')
                ax.legend()

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                line_plot_uri = urllib.parse.quote(string)

                 # Box plot
                fig, ax = plt.subplots()
                ax.boxplot(wert1)
                ax.set_title(f'Box Plot of Wert - {location1}')
                ax.set_ylabel('Wert')

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                box_plot_uris.append(urllib.parse.quote(string))

                # second box plot
                fig, ax = plt.subplots()
                ax.boxplot(wert2)
                ax.set_title(f'Box Plot of Wert - {location2}')
                ax.set_ylabel('Wert')

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                box_plot_uris.append(urllib.parse.quote(string))

                # Bar plot
                mean1 = sum(wert1) / len(wert1) if wert1 else 0
                mean2 = sum(wert2) / len(wert2) if wert2 else 0
                fig, ax = plt.subplots()
                ax.bar([location1, location2], [mean1, mean2], color=['cyan', 'magenta'])
                ax.set_title('Comparison of Mean Values')
                ax.set_ylabel('Mean Wert')

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                bar_plot_uri = urllib.parse.quote(string)

            else:
                location = locations[0]
                max_agg = Station.objects.filter(messstelle=location).values('id').aggregate(max_num=Max('id'))
                st_id = max_agg.get('max_num', 1)
                data = Measurement.objects.filter(timestamp__date__range=(start_date, end_date), station_id=st_id).values('timestamp', 'wert')
                wert = list(map(lambda d: d['wert'], data))
                dates = list(map(lambda d: d['timestamp'], data))
                p_bcg = r'.\floodapp\static\images\graph_background2.webp'

                # Line plot
                img = plt.imread(p_bcg)
                fig, ax = plt.subplots()
                ax.imshow(img, extent=[min(dates), max(dates), min(wert), max(wert)], aspect='auto', zorder=0)
                ax.plot(dates, wert, 'bo-', label='wert', color='cyan', zorder=1)
                ax.set_xlabel('Date')
                ax.set_ylabel('Wert')

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                line_plot_uri = urllib.parse.quote(string)

                # Box plot
                fig, ax = plt.subplots()
                ax.boxplot(wert1 if len(locations) == 2 else wert)
                ax.set_title('Box Plot of Wert')
                ax.set_ylabel('Wert')

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                box_plot_uris.append(urllib.parse.quote(string))
                return render(request, 'historical_data_graph.html', {'form': form, 'line_plot': line_plot_uri, 'box_plots': box_plot_uris})

            return render(request, 'historical_data_graph.html', {'form': form, 'line_plot': line_plot_uri, 'box_plots': box_plot_uris, 'bar_plot': bar_plot_uri})

    else:
        form = GraphParametersForm()
    return render(request, 'historical_data_graph.html', {'form': form})



def search_location(request):
    location = request.GET.get('location')
    payload = []
    if location:
        locs = Station.objects.filter(messstelle__icontains = location)
        for loc in locs:
            payload.append(loc.messstelle)

    return JsonResponse({'status': 200, 'data': payload})