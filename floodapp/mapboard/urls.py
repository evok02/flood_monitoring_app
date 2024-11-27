from django.urls import path
from . import views

urlpatterns = [
    path('', views.water_levels_api, name='map'),
    path('admin_only_page/', views.admin_only_page, name='admin_only_page')
]       