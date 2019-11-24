from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ValidationError
from textwrap import dedent

from lists.models import Item, List
from lists.forms import ExistingListItemForm, NewListFromItemForm, SharingForm
from django.contrib.auth import get_user_model
User = get_user_model()


def home_page(request):
    return render(request, 'home.html', {'form': NewListFromItemForm()})


def view_list(request, list_id):
    def authorized():
        is_public_list = not list_.owner
        if is_public_list:
            return True

        if not request.user.is_authenticated:
            return False

        if list_.owner == request.user:
            return True

        list_shared_with_logged_in_user = list_.sharees.filter(
            email=request.user.email
        ).exists()
        if list_shared_with_logged_in_user:
            return True

        return False

    list_ = List.objects.get(id=list_id)

    if not authorized():
        raise Http404()

    item = Item(list=list_)
    form = ExistingListItemForm()
    if request.method == 'POST':
        form = ExistingListItemForm(instance=item, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, 'form': form, 'sharing_form': SharingForm()})


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
    def is_authorized(user):
        if not user.is_authenticated:
            return False
        if user.email != user_email:
            return False
        return True

    if not is_authorized(request.user):
        raise Http404()

    owner = User.objects.get(email=user_email)
    return render(request, 'my_lists.html', {'owner': owner})


def share(request, list_id):
    sharing_form = SharingForm(list_id=list_id, data=request.POST)
    sharing_form.is_valid()
    updated_list = sharing_form.save()
    return redirect(updated_list)
