from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.views.generic import FormView, CreateView
from textwrap import dedent

from lists.models import Item, List
from lists.forms import ExistingListItemForm, NewListFromItemForm
from django.contrib.auth import get_user_model
User = get_user_model()


class HomePageView(FormView):
    template_name = 'home.html'
    form_class = NewListFromItemForm


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


class NewListView(CreateView):
    form_class = NewListFromItemForm
    template_name = 'home.html'

    def get_form_kwargs(self):
        if self.request.user.is_authenticated:
            return {'data': self.request.POST, 'owner': self.request.user}
        else:
            return {'data': self.request.POST}

    def form_valid(self, form):
        list_ = form.save()
        return redirect(list_)

    def form_invalid(self, form):
        return render(self.request, 'home.html', {'form': form})


def my_lists(request, user_email):
    owner = User.objects.get(email=user_email)
    return render(request, 'my_lists.html', {'owner': owner})
