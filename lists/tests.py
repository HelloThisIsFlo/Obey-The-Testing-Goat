from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string

from lists.views import home_page
from lists.models import Item, TodoList

from superlists.features import feature_flags


class HomePageTest(TestCase):
    def test_go_home_creates_new_list(self):
        self.assertEqual(TodoList.objects.count(), 0)
        self.client.get('/')
        self.assertEqual(TodoList.objects.count(), 1)

    def test_go_home_redirects_to_list_url(self):
        response = self.client.get('/')
        new_list_id = TodoList.objects.first().id
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f'/lists/{new_list_id}')


class MultiUser_TodoListPageTest(TestCase):
    def setUp(self):
        self.list = TodoList()
        self.list.save()

    def test_list_page_return_correct_template(self):
        response = self.client.get(f'/lists/{self.list.id}')
        self.assertTemplateUsed(response, 'todo_list.html')

    def test_list_page_displays_list(self):
        Item.objects.create(todo_list=self.list, text='itemey 1')
        Item.objects.create(todo_list=self.list, text='itemey 2')

        response = self.client.get(f'/lists/{self.list.id}')

        content = response.content.decode()
        self.assertIn('itemey 1', content)
        self.assertIn('itemey 2', content)

    def test_can_add_item_with_POST(self):
        self.client.post(
            f'/lists/{self.list.id}/add_item',
            data={'item_text': 'A new list item'}
        )
        self.assertEqual(self.list.item_set.count(), 1)
        new_item = self.list.item_set.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_adding_item_with_POST(self):
        response = self.client.post(
            f'/lists/{self.list.id}/add_item',
            data={'item_text': 'A new list item'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f'/lists/{self.list.id}')

    def test_return_404_when_trying_to_display_nonexisting_list(self):
        nonexisting_list_id = 12345
        response = self.client.get(f'/lists/{nonexisting_list_id}')

        self.assertEqual(response.status_code, 404)

    def test_return_404_when_trying_to_add_item_to_nonexisting_list(self):
        nonexisting_list_id = 12345
        response = self.client.get(f'/lists/{nonexisting_list_id}/add_item')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Item.objects.count(), 0)


class ItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        todo_list = TodoList()
        todo_list.save()

        first_item = Item()
        first_item.todo_list = todo_list
        first_item.text = 'The first (ever) list item'
        first_item.save()

        second_item = Item()
        second_item.todo_list = todo_list
        second_item.text = 'Item the second'
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        self.assertEqual(second_saved_item.text, 'Item the second')

    def test_deleting_list_deletes_all_items(self):
        todo_list = TodoList()
        todo_list.save()
        Item.objects.create(todo_list=todo_list, text='itemey 1')
        Item.objects.create(todo_list=todo_list, text='itemey 2')
        self.assertEqual(Item.objects.count(), 2)

        todo_list.delete()

        self.assertEqual(Item.objects.count(), 0)
