from django.db import models


class TodoList(models.Model):
    pass


class Item(models.Model):
    text = models.TextField(default='')
    # TODO: Remove `null=True` when multi-user feature completed
    todo_list = models.ForeignKey(TodoList, null=True)
