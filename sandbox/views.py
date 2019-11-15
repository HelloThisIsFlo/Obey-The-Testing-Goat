from django.shortcuts import render, redirect, HttpResponse, reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required


def main(request):
    return render(request, 'sandbox/main.html', {'next': request.GET.get('next')})


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

    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return redirect('sandbox_main')


@login_required(login_url='/sandbox/')
def private(request):
    # This is a private page only accessible to logged in users
    return render(request, 'sandbox/private.html')


def logout(request):
    auth.logout(request)
    return redirect('sandbox_main')
