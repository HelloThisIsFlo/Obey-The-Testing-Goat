from django.shortcuts import render
from django.http import HttpResponse
from textwrap import dedent


def home_page(request):
    item_text = request.POST.get('item_text', '')
    return render(request, 'home.html', {'new_item_text': item_text})
