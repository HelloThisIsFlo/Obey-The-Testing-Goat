from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.views.generic import FormView, CreateView, DetailView
from textwrap import dedent

from lists.models import Item, List
from lists.forms import ExistingListItemForm, NewListFromItemForm
from django.contrib.auth import get_user_model
User = get_user_model()


class HomePageView(FormView):
    template_name = 'home.html'
    form_class = NewListFromItemForm


class ViewAndAddToList(DetailView, CreateView):
    model = List
    template_name = 'list.html'
    form_class = ExistingListItemForm

    def get_form_kwargs(self):
        self.object = self.get_object()
        item = Item(list=self.object)
        return {'instance': item, 'data': self.request.POST}


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
