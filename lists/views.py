from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from textwrap import dedent

from lists.models import Item, List
from lists.forms import ItemForm, NewListFromItemForm


def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    item = Item(list=list_)
    form = ItemForm()
    if request.method == 'POST':
        form = ItemForm(instance=item, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, 'form': form})


def new_list(request):
    list_ = List.objects.create()
    item = Item(list=list_)
    form = ItemForm(instance=item, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(list_)
    else:
        list_.delete()
        return render(request, 'home.html', {'form': form})

def new_list2(request):
    form = NewListFromItemForm(first_list_item=request.POST['text'])
    if form.is_valid():
        form.save()
        return redirect(form.saved_list)
    else:
        return render(request, 'home.html', {'form': form})


def my_lists(request):
    return render(request, 'my_lists.html', {'owner': request.user})