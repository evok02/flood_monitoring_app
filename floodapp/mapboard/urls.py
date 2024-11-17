from django.urls import path
from . import views

urlpatterns = [
    path('', views.water_levels_api, name='map'),
]