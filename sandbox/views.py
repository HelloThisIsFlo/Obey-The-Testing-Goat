from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth


def main(request):
    return render(request, 'sandbox/main.html')


def login(request):
    user = auth.authenticate(
        request,
        username=request.POST['username'],
        password=request.POST['pass']
    )
    if user is None:
        print('auth failed')
    else:
        auth.login(request, user)

    return redirect('sandbox_main')


def logout(request):
    auth.logout(request)
    return redirect('sandbox_main')
