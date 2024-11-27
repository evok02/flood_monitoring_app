from django.urls import path
from . import views

urlpatterns = [
    path('', views.water_levels_api, name='map'),
    path('history/<int:region_id>/', views.water_level_history, name='water-level-history'),
    path('report-emergency/', views.report_emergency, name='report-emergency')
]