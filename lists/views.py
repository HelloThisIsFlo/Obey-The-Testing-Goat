from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from textwrap import dedent

from lists.models import Item, List
from lists.forms import ExistingListItemForm, NewListForm
User = get_user_model()


def home_page(request):
    return render(request, 'home.html', {'form': NewListForm()})


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)
    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, 'form': form})


def new_list(request):
    new_list_form = NewListForm(owner=request.user, data=request.POST)
    if new_list_form.is_valid():
        list_ = new_list_form.save()
        return redirect(list_)
    else:
        return render(request, 'home.html', {'form': new_list_form})


def my_lists(request, user_email):
    owner = User.objects.get(pk=user_email)
    return render(request, 'my_lists.html', {'owner': owner})
