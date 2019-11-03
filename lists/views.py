from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from textwrap import dedent

from lists.models import Item, TodoList
from superlists.features import feature_flags


def home_page(request):
    new_list = TodoList()
    new_list.save()
    return redirect(f'/lists/{new_list.id}')


def list_page(request, list_id):
    return render(
        request,
        'todo_list.html',
        {'todo_list': get_object_or_404(TodoList, id=list_id)}
    )


def add_item(request, list_id):
    todo_list = get_object_or_404(TodoList, id=list_id)
    Item.objects.create(todo_list=todo_list, text=request.POST['item_text'])
    return redirect('list', list_id=list_id)
