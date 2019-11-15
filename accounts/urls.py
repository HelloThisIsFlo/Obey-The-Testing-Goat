from django.conf.urls import url
from django.contrib import admin
from accounts import views

urlpatterns = [
    url(r'^send_login_email$', views.send_login_email, name='send_login_email'),
]
