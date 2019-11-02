from django.shortcuts import render, redirect
from django.http import HttpResponse
from textwrap import dedent

from lists.models import Item


def home_page(request):
    if request.method == 'POST':
        new_item_text = request.POST['item_text']
        Item.objects.create(text=new_item_text)
    else:
        new_item_text = ''

    return render(request, 'home.html', {'new_item_text': new_item_text})
