from importlib import import_module
from django.conf import settings
from django.contrib import auth
User = auth.get_user_model()
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('email')

    def handle(self, *args, **options):
        session_key = create_pre_authenticated_session(options['email'])
        self.stdout.write(session_key)

def create_pre_authenticated_session(email):
    user = User.objects.create(email=email)
    session = SessionStore()
    session[auth.SESSION_KEY] = user.pk
    session[auth.BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session.save()
    return session.session_key
