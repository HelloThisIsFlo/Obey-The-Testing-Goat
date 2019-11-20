from unittest.mock import patch
from unittest import skip
import unittest
from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from lists.views import home_page, new_list
from lists.models import Item, List
from lists.forms import NewListForm, ExistingListItemForm, EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR
User = get_user_model()


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_uses_new_list_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], NewListForm)


class ListViewTest(TestCase):
    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_passes_correct_list_to_template(self):
        # # I'd argue this test is unnecessary since it's already covered by
        # # a functional test, and in some ways by 'test_displays_only_items_for_that_list'
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def test_for_invalid_input_nothing_saved_to_db(self):
        response = self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_duplicate_item_shows_error_on_page(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='duplicate')
        response = self.client.post(
            f'/lists/{list_.id}/',
            data={'text': 'duplicate'}
        )
        self.assertContains(response, escape(DUPLICATE_ITEM_ERROR))

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')


class NewListViewIntegratedTest(TestCase):
    def test_can_save_a_POST_request(self):
        response = self.client.post(
            '/lists/new',
            data={'text': 'A new list item'}
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_on_error_validation_errors_are_show_on_home_page_and_nothing_is_saved(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item text'})
        self.assertEqual(user.list_set.first().name, 'new item text')


@patch('lists.views.NewListForm')
class NewListViewUnitTest(unittest.TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = AnonymousUser

    def test_passes_POST_data_and_current_user_to_NewListForm(self, MockNewListFormClass):
        new_list(self.request)
        MockNewListFormClass.assert_called_once_with(
            owner=self.request.user,
            data=self.request.POST
        )

    def test_saves_form_if_form_valid(self, MockNewListFormClass):
        mock_form = MockNewListFormClass.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once()

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(
        self,
        mock_redirect,
        MockNewListFormClass
    ):
        mock_form = MockNewListFormClass.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)

        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)

    @patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(
        self,
        mock_render,
        MockNewListFormClass
    ):
        mock_form = MockNewListFormClass.return_value
        mock_form.is_valid.return_value = False

        response = new_list(self.request)

        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            self.request, 'home.html', {'form': mock_form})

    def test_does_not_save_if_form_invalid(self, MockNewListFormClass):
        mock_form = MockNewListFormClass.return_value
        mock_form.is_valid.return_value = False

        new_list(self.request)

        mock_form.save.assert_not_called()


class MyListsTest(TestCase):
    def test_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'my_lists.html')

    def test_passes_correct_owner_to_template(self):
        _ = User.objects.create(email='not_the_owner@list.com')
        owner = User.objects.create(email='owner@list.com')
        response = self.client.get('/lists/users/owner@list.com/')
        self.assertEqual(response.context['owner'], owner)
