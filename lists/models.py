from django.db import models


class TodoList(models.Model):
    pass


class Item(models.Model):
    text = models.TextField(default='')
    todo_list = models.ForeignKey(TodoList)
