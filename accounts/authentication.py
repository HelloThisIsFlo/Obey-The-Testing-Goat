from accounts.models import User, Token


def exists(model_class, **kwargs):
    return model_class.objects.filter(**kwargs).exists()


class PasswordlessAuthenticationBackend():
    def authenticate(self, uid):
        if not exists(Token, uid=uid):
            return None

        token = Token.objects.get(uid=uid)

        if exists(User, email=token.email):
            existing_user = User.objects.get(email=token.email)
            return existing_user
        else:
            new_user = User.objects.create(email=token.email)
            return new_user

    def authenticate_book_version(self, uid):
        try:
            token = Token.objects.get(uid=uid)
            existing_user = User.objects.get(email=token.email)
            return existing_user
        except Token.DoesNotExist:
            return None
        except User.DoesNotExist:
            new_user = User.objects.create(email=token.email)
            return new_user

    def get_user(self, email):
        if not exists(User, email=email):
            return None

        return User.objects.get(email=email)
