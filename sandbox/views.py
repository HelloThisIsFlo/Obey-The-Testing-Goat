from django.shortcuts import render, HttpResponse, redirect
import uuid

session_template = {
    'logged_in': False,
    'email': 'frank@frank.com',
    'login_token': 'asdfasdf134dsfasdf'
}

CODE_EXPIRATION = 15
SESSION_EXPIRATION = 60


def main(request):
    if request.session.get('logged_in', False) is True:
        print(request.session.get_expiry_date())
        return render(request, 'sandbox/private.html', {'session': request.session})
    else:
        return redirect('sandbox_login')


def login(request):
    print(request)
    email_sent = False

    if request.method == 'POST':
        email = request.POST['email']
        code = uuid.uuid4().hex
        request.session['email'] = email
        request.session['code'] = code
        request.session.set_expiry(CODE_EXPIRATION)
        send_email(email, code)
        email_sent = True

    else:
        def auth_link_valid():
            if 'email' not in request.session or 'code' not in request.session:
                return False

            link_email = request.GET.get('email', '')
            link_code = request.GET.get('code', '')
            session_email = request.session['email']
            session_code = request.session['code']
            return link_email == session_email and link_code == session_code

        if auth_link_valid():
            request.session['logged_in'] = True
            request.session.set_expiry(SESSION_EXPIRATION)
            return redirect('sandbox_main')

    return render(request, 'sandbox/login.html', {'email_sent': email_sent})


def send_email(email, code):
    print(
        f'Go to http://localhost:8000/sandbox/login?email={email}&code={code}')
    print(f'Warning the code is only valid for {CODE_EXPIRATION} seconds!')
