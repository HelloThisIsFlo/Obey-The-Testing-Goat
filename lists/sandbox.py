from django.shortcuts import render
from django import forms
from lists.models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'author',  'pub_date']


def sandbox(request):
    submitted_data = {}

    form = ArticleForm()
    if request.method == 'POST':
        form = ArticleForm(request.POST)

    return render(request, 'sandbox.html',  {'form': form, 'submitted': request.POST})
