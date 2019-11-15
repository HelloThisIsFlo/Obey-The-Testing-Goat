from django.shortcuts import render, redirect
from django.core.mail import send_mail


def send_login_email(request):
    email = request.POST['email']
    send_mail(
        'Your login link for Superlists',
        'TODO',
        'noreply@superlists',
        [email]
    )
    return redirect('/')
