from django.shortcuts import render, redirect
from django.http import HttpResponse
from textwrap import dedent

from lists.models import Item, List
from superlists.features import feature_flags


def home_page(request):
    if request.method == 'POST':
        Item.objects.create(text=request.POST['item_text'])
        return redirect('/')

    if feature_flags.multiple_lists:
        new_list = List()
        new_list.save()
        return redirect(f'/lists/{new_list.id}')

    return render(request, 'home.html', {'items': Item.objects.all()})


def list_page(request, list_id):
    return render(
        request,
        'list.html',
        {'list': List.objects.get(id=list_id)}
    )

def add_item(request, list_id):
    todo_list = List.objects.get(id=list_id)
    Item.objects.create(todo_list=todo_list, text=request.POST['item_text'])
    return HttpResponse('ok')
