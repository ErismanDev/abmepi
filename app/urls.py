# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('download-carne/', views.download_carne, name='download_carne'),
]
