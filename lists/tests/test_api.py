import json
from django.test import TestCase

from lists.models import List, Item


def list_url(list_id):
    return f'/api/lists/{list_id}/'


class ListAPITest(TestCase):
    def test_get_returns_json_200(self):
        list_ = List.objects.create()
        response = self.client.get(list_url(list_.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_returns_items_for_correct_list(self):
        other_list = List.objects.create()
        Item.objects.create(list=other_list, text='item 1')
        our_list = List.objects.create()
        item1 = Item.objects.create(list=our_list, text='item 1')
        item2 = Item.objects.create(list=our_list, text='item 2')

        response = self.client.get(list_url(our_list.id))

        self.assertEqual(
            json.loads(response.content.decode('utf8')),
            [
                {'id': item1.id, 'text': item1.text},
                {'id': item2.id, 'text': item2.text},
            ]
        )

    def test_POSTing_a_new_item(self):
        list_ = List.objects.create()

        response = self.client.post(list_url(list_.id), {'text': 'new item'})

        self.assertEqual(response.status_code, 201)
        new_item = list_.item_set.first()
        self.assertEqual(new_item.text, 'new item')