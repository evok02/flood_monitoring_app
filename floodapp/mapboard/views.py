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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
logger = logging.getLogger('flood_app')
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects
import matplotlib.dates as mdates
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

@csrf_exempt
def report_emergency(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Received report data: {data}")

            # Extract fields
            description = data.get('description')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            urgency_level = data.get('urgency_level')

            # Validate inputs
            if not description or not urgency_level or latitude is None or longitude is None:
                logger.error("Validation failed: Missing required fields.")
                return JsonResponse({'success': False, 'error': 'All fields are required.'})

            # Create and save the report without assigning a region
            report = EmergencyReport.objects.create(
                description=description,
                urgency_level=urgency_level,
                latitude=latitude,
                longitude=longitude
            )
            logger.info(f"Report created successfully with ID: {report.id}")

            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error in report_emergency: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

# Endpoint to return all emergency reports in JSON format
def get_emergency_reports(request):
    reports = EmergencyReport.objects.exclude(latitude__isnull=True, longitude__isnull=True)

    data = [
        {
            "id": report.id,
            "description": report.description,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "urgency_level": report.urgency_level,
            "timestamp": report.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for report in reports
    ]

    return JsonResponse(data, safe=False)

def fetch_emergencies_view(request):
        emergencies = EmergencyReport.objects.select_related('region').all()
        data = [
            {
                "region": emergency.region.name if emergency.region else None,
                "description": emergency.description,
                "latitude": emergency.region.latitude,
                "longitude": emergency.region.longitude,
                "location": emergency.location,
                "urgency_level": emergency.urgency_level,
            }
            for emergency in emergencies
        ]
        return JsonResponse(data, safe=False)

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

@login_required
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


                # Line plot
                fig, ax = plt.subplots()
                ax.plot(dates1, wert1, 'bo-', label=location1, color='#007BFF', zorder=1)
                ax.plot(dates2, wert2, 'ro-', label=f'{location2}', color='#FF8800', zorder=1)
                ax.set_facecolor("#1E2A38")
                ax.grid(color='#3A4755', linestyle='--', linewidth=0.5, alpha=0.7)
                for line in ax.get_lines():
                    line.set_path_effects([
                        patheffects.withStroke(linewidth=4, foreground="black", alpha=0.3)
                    ])
                fig.patch.set_facecolor('#2A3B4C')
                ax.set_xlabel('Date', color='white')
                ax.set_ylabel('Wert', color='white')
                ax.tick_params(axis='x', colors='white') 
                ax.tick_params(axis='y', colors='white')

                locator = mdates.AutoDateLocator()
                formatter = mdates.AutoDateFormatter(locator)
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(formatter)

                plt.xticks(rotation=45) 

                ax.legend()

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                line_plot_uri = urllib.parse.quote(string)

                 # Box plot
                fig, ax = plt.subplots()
                ax.boxplot(wert1,
                    patch_artist=True,
                    boxprops=dict(facecolor='#007BFF', color='white'),
                    whiskerprops=dict(color='#FF8800', linewidth=1.5), 
                    capprops=dict(color='#FF8800', linewidth=2),  
                    flierprops=dict(marker='o', markerfacecolor='red', markeredgecolor='black', markersize=8), 
                    medianprops=dict(color='white', linewidth=2))  
                fig.patch.set_facecolor('#2A3B4C')
                ax.grid(color='#3A4755', linestyle='--', linewidth=0.5, alpha=0.7)
                ax.set_facecolor("#1E2A38")
                ax.set_title(f'Box Plot of Wert - {location1}', color='white')
                ax.set_ylabel('Wert', color='white')
                ax.tick_params(axis='y', colors='white')

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                box_plot_uris.append(urllib.parse.quote(string))

                # second box plot
                fig, ax = plt.subplots()
                ax.boxplot(wert2,
                    patch_artist=True, 
                    boxprops=dict(facecolor='#007BFF', color='white'), 
                    whiskerprops=dict(color='#FF8800', linewidth=1.5),  
                    capprops=dict(color='#FF8800', linewidth=2),  
                    flierprops=dict(marker='o', markerfacecolor='red', markeredgecolor='black', markersize=8), 
                    medianprops=dict(color='white', linewidth=2))  
                fig.patch.set_facecolor('#2A3B4C')
                ax.grid(color='#3A4755', linestyle='--', linewidth=0.5, alpha=0.7)
                ax.set_facecolor("#1E2A38")
                ax.set_title(f'Box Plot of Wert - {location2}', color='white')
                ax.set_ylabel('Wert', color='white')
                ax.tick_params(axis='y', colors='white')

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                box_plot_uris.append(urllib.parse.quote(string))

                # Bar plot
                mean1 = sum(wert1) / len(wert1) if wert1 else 0
                mean2 = sum(wert2) / len(wert2) if wert2 else 0
                fig, ax = plt.subplots()
                ax.bar([location1, location2], [mean1, mean2], color=['#007BFF', '#FF8800'], zorder=3)
                fig.patch.set_facecolor('#2A3B4C')
                ax.grid(color='#3A4755', linestyle='--', linewidth=0.5, alpha=0.7, zorder=0)
                ax.set_facecolor("#1E2A38")
                ax.set_title('Comparison of Mean Values', color='white')
                ax.set_ylabel('Mean Wert', color='white')
                ax.tick_params(axis='x', colors='white') 
                ax.tick_params(axis='y', colors='white')

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
                p_bcg = r'floodapp/static/images/graph_background2.webp'

                # Line plot
                plt.figure(figsize=(12,8))
                img = plt.imread(p_bcg)
                fig, ax = plt.subplots()
                # ax.imshow(extent=[min(dates), max(dates), min(wert), max(wert)], aspect='auto', zorder=0)
                ax.plot(dates, wert, 'bo-', label=location, color='#007BFF', zorder=1)
                ax.set_facecolor("#1E2A38")
                ax.grid(color='#3A4755', linestyle='--', linewidth=0.5, alpha=0.7)
                for line in ax.get_lines():
                    line.set_path_effects([
                        patheffects.withStroke(linewidth=4, foreground="black", alpha=0.3)
                    ])
                fig.patch.set_facecolor('#2A3B4C')
                ax.set_xlabel('Date', color='white')
                ax.set_ylabel('Wert', color='white')
                ax.tick_params(axis='x', colors='white') 
                ax.tick_params(axis='y', colors='white')
                locator = mdates.AutoDateLocator()
                formatter = mdates.AutoDateFormatter(locator)
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(formatter)
                plt.xticks(rotation=45)
                plt.legend()
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                line_plot_uri = urllib.parse.quote(string)

                # Box plot
                fig, ax = plt.subplots()
                ax.boxplot(wert1 if len(locations) == 2 else wert,
                    patch_artist=True, 
                    boxprops=dict(facecolor='#007BFF', color='white'), 
                    whiskerprops=dict(color='#FF8800', linewidth=1.5), 
                    capprops=dict(color='#FF8800', linewidth=2),  
                    flierprops=dict(marker='o', markerfacecolor='red', markeredgecolor='black', markersize=8),
                    medianprops=dict(color='white', linewidth=2)) 
                fig.patch.set_facecolor('#2A3B4C')
                ax.grid(color='#3A4755', linestyle='--', linewidth=0.5, alpha=0.7)
                ax.set_facecolor("#1E2A38")
                ax.set_title(f'Box Plot of {location}', color='white')
                ax.set_ylabel('Wert', color='white')
                ax.tick_params(axis='y', colors='white')

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