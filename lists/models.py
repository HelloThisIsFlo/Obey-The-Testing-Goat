from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class List(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=None,
        null=True
    )

    sharees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='+'
    )

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])

    def add_sharee(self,  email):
        sharee = User.objects.get(email=email)
        self.sharees.add(sharee)

    @staticmethod
    def create_new(first_item_text, owner=None):
        list_ = List.objects.create(owner=owner)
        Item.objects.create(list=list_, text=first_item_text)
        return list_

    @property
    def name(self):
        return self.item_set.first().text


class Item(models.Model):
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None)

    class Meta:
        ordering = ('id',)
        unique_together = ('list', 'text',)

    def __str__(self):
        return self.text
