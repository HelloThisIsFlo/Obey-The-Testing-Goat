from django.shortcuts import render, HttpResponse


def main(request):
    if request.method == 'POST':
        data = {'email': request.POST['email']}
    else:
        data = {}

    return render(request, 'sandbox/main.html', data)
