from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ValidationError
from textwrap import dedent

from lists.models import Item, List
from lists.forms import NewItemWithExistingListForm, NewListFromItemForm, SharingForm
from django.contrib.auth import get_user_model
User = get_user_model()


def _authorized_to_access_list(user, list_):
    is_public_list = not list_.owner
    if is_public_list:
        return True

    if not user.is_authenticated:
        return False

    if list_.owner == user:
        return True

    list_shared_with_logged_in_user = list_.sharees.filter(
        email=user.email
    ).exists()
    if list_shared_with_logged_in_user:
        return True

    return False


def home_page(request):
    return render(request, 'home.html', {'form': NewListFromItemForm()})


def view_list(request, list_id):
    def is_new_item_form():
        return 'text' in request.POST

    def render_view_list(list_, new_item_form=None, sharing_form=None):
        if not new_item_form:
            new_item_form = NewItemWithExistingListForm()

        if not sharing_form:
            sharing_form = SharingForm()

        return render(
            request,
            'list.html',
            {'list': list_, 'form': new_item_form, 'sharing_form': sharing_form}
        )

    def handle_new_item_form(list_):
        new_item_form = NewItemWithExistingListForm(list_=list_, data=request.POST)
        if new_item_form.is_valid():
            new_item_form.save()
            return redirect(list_)

        return render_view_list(list_, new_item_form=new_item_form)

    def handle_sharing_form(list_):
        raise 'not implemented'

    list_ = List.objects.get(id=list_id)

    if not _authorized_to_access_list(request.user, list_):
        raise Http404()

    if request.method == 'POST':
        if is_new_item_form():
            return handle_new_item_form(list_)
        else:
            return handle_sharing_form(list_)
    else:
        return render_view_list(list_)


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
    list_ = List.objects.get(id=list_id)
    sharing_form = SharingForm(list_=list_, data=request.POST)
    sharing_form.is_valid()
    updated_list = sharing_form.save()
    return redirect(updated_list)
