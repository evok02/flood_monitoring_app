from django.urls import path
from . import views

urlpatterns = [
    path('', views.mapboard_view, name='map'),
]