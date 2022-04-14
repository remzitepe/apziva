from operator import index
from django import views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("home", views.index),
    path("github_details", views.github_details),
    path("github", views.github),
    path("about", views.about),
    path("stackoverflow_details", views.stackoverflow_details),
    path("stackoverflow", views.stackoverflow)
]