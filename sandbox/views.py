from django.shortcuts import render, HttpResponse, redirect


def main(request):
    if request.method == 'POST':
        request.session['email'] = request.POST['email']
        return redirect('sandbox_main')

    if 'email' in request.session:
        data = {'email': request.session['email']}
    else:
        data = {}

    return render(request, 'sandbox/main.html', data)


def send_email(email, code):
    print(
        f'Go to http://localhost:8000/sandbox/login?email={email}&code={code}')
