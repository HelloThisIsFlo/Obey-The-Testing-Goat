from django.conf.urls import url
from django.contrib import admin
from sandbox import views

urlpatterns = [
    url(r'^main$', views.main, name='sandbox_main'),
    url(r'^login$', views.login, name='sandbox_login'),
]
