from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from uuid import uuid4


class User(models.Model):
    email = models.EmailField(primary_key=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    is_anonymous = False
    is_authenticated = False


class Token(models.Model):
    email = models.EmailField()
    uid = models.CharField(default=uuid4, max_length=250)
