from django.urls import path
from . import views

urlpatterns = [
    path('', views.water_levels_api, name='map'),
    path('history/<int:region_id>/', views.water_level_history, name='water-level-history'),
    path('report-emergency/', views.report_emergency_view, name='report-emergency'),
    path('admin_only_page/', views.admin_only_page, name='admin_only_page'),
    path('schedule/', views.task_scheduling_page, name='task_scheduling_page'),
    path('add-event/', views.add_event, name='add_event'),
    path('api/events/', views.event_list, name='event_list'),
    path('delete_event/', views.delete_event, name='delete_event'),
    path('update_event/', views.update_event, name='update_event'),
]