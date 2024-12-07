from django.urls import path
from . import views

urlpatterns = [
    path('', views.water_levels_api, name='map'),
    path('water-map/', views.waterlevel_map, name='waterlevel-map'),
    path('history/<int:region_id>/', views.water_level_history, name='water-level-history'),
    path('report-emergency/', views.report_emergency_view, name='report-emergency'),
    path('admin_only_page/', views.admin_only_page, name='admin_only_page'),
    path('historical-data/', views.historical_data_view, name='historical_data')
]