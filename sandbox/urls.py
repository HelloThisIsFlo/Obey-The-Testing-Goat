from django.conf.urls import url
from django.contrib import admin
from sandbox import views

urlpatterns = [
    url(r'^$', views.main, name='sandbox_main'),
]
