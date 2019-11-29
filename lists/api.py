import json

from django.http import HttpResponse
from rest_framework import routers, serializers, viewsets,  generics, mixins
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from lists.models import List, Item
from lists.forms import ExistingListItemForm, EMPTY_ITEM_ERROR


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'text', 'list']


class ListSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, source='item_set', read_only=True)

    class Meta:
        model = List
        fields = ['id', 'items']


class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


router = DefaultRouter()
router.register(r'lists', ListViewSet)
router.register(r'items', ItemViewSet)
