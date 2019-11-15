from django.conf.urls import url
from django.contrib import admin
from sandbox import views

urlpatterns = [
    url(r'^main$', views.main, name='main'),
]
