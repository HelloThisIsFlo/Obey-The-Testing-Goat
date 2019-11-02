from django.shortcuts import render
from django.http import HttpResponse
from textwrap import dedent

from lists.models import Item


def home_page(request):
    item = Item()
    item.text = request.POST.get('item_text', '')
    item.save()

    return render(request, 'home.html', {'new_item_text': item.text})
