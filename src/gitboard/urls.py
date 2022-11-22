from django.contrib import admin
from django.urls import path
from gitboard.views import index, favicon

urlpatterns = [
    path('', index, name="index"),
    path( "favicon.ico/", favicon, name="favicon"),
]