from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ValidationError
from textwrap import dedent

from lists.models import Item, List
from lists.forms import ExistingListItemForm, NewListFromItemForm
from django.contrib.auth import get_user_model
User = get_user_model()


def home_page(request):
    return render(request, 'home.html', {'form': NewListFromItemForm()})


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    item = Item(list=list_)
    form = ExistingListItemForm()
    if request.method == 'POST':
        form = ExistingListItemForm(instance=item, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, 'form': form})


def new_list(request):
    if request.user.is_authenticated:
        form = NewListFromItemForm(data=request.POST, owner=request.user)
    else:
        form = NewListFromItemForm(data=request.POST)

    if form.is_valid():
        saved_list = form.save()
        return redirect(saved_list)
    else:
        return render(request, 'home.html', {'form': form})


def my_lists(request, user_email):
    if not request.user.is_authenticated:
        raise Http404()

    owner = User.objects.get(email=user_email)
    return render(request, 'my_lists.html', {'owner': owner})
