import sys
from accounts.models import ListUser, Token

class PasswordlessAuthenticationBackend:
    def get_user(self, email):
        return ListUser.objects.get(email=email)

    def authenticate(self, _request, uid=None):
        if not Token.objects.filter(uid=uid).exists():
            print('No matching token found', file=sys.stderr)
            return None

        token = Token.objects.get(uid=uid)
        email = token.email
        if ListUser.objects.filter(email=email).exists():
            return ListUser.objects.get(email=email)
        else:
            return ListUser.objects.create_user(email)
