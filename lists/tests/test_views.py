from unittest.mock import patch
import unittest
from lists.forms import ItemForm, EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR
from lists.models import Item, List
from lists.views import home_page, my_lists, new_list2
from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth import get_user_model
User = get_user_model()


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


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
        self.assertIsInstance(response.context['form'], ItemForm)

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
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertContains(response, 'name="text"')


class NewListIntegratedTest(TestCase):
    def test_can_save_a_POST_request(self):
        response = self.client.post(
            '/lists/new',
            data={'text': 'A new list item'}
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post(
            '/lists/new',
            data={'text': 'A new list item'}
        )
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_validation_errors_are_show_on_home_page(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(Item.objects.count(), 0)
        self.assertEqual(List.objects.count(), 0)


@patch('lists.views.redirect')
@patch('lists.views.NewListFromItemForm')
class NewListTest(unittest.TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'TEXT'

    # @patch('lists.views.List')
    # @patch('lists.views.Item')
    # @patch('lists.views.ItemForm')
    # @patch('lists.views.redirect')
    # def test_valid_data__create_new_list(
    #     self,
    #     MockList,
    #     MockItem,
    #     MockItemForm,
    #     mock_redirect
    # ):
    #     form = MockItemForm.return_value
    #     self.request.POST['text'] = 'A new list item'

    #     new_list2(self.request)

    #     MockList.objects.create.assert_called_once()
    #     MockItem.assert_called_once_with(
    #         list=MockList.objects.create.return_value
    #     )
    #     MockItemForm.assert_called_once_with(
    #         instance=MockItem.return_value,
    #         data=self.request.POST
    #     )
    #     form.is_valid.assert_called_once()
    #     form.save.assert_called_once()

    def test_valid_data__create_new_list(
        self,
        MockNewListFromItemForm,
        mock_redirect
    ):
        self.request.POST['text'] = 'A new list item'

        new_list2(self.request)

        MockNewListFromItemForm.assert_called_once_with(
            first_list_item='A new list item')
        form = MockNewListFromItemForm.return_value
        form.is_valid.assert_called_once()
        form.save.assert_called_once()

    def test_valid_data__redirects_to_new_list(
        self,
        MockNewListFromItemForm,
        mock_redirect
    ):
        response = new_list2(self.request)

        form = MockNewListFromItemForm.return_value
        newly_created_list = form.saved_list
        mock_redirect.assert_called_once_with(newly_created_list)
        self.assertEqual(response, mock_redirect.return_value)


    @patch('lists.views.render')
    def test_invalid_data__renders_home_template_with_form_containing_errors(
        self,
        mock_render,
        MockNewListFromItemForm,
        mock_redirect
    ):
        form_with_errors = MockNewListFromItemForm.return_value
        form_with_errors.is_valid.return_value = False

        response = new_list2(self.request)

        mock_render.assert_called_once_with(self.request, 'home.html', {'form': form_with_errors})
        self.assertEqual(response, mock_render.return_value)

    def test_invalid_data__form_is_not_saved(
        self,
        MockNewListFromItemForm,
        mock_redirect
    ):
        form_with_errors = MockNewListFromItemForm.return_value
        form_with_errors.is_valid.return_value = False

        new_list2(self.request)

        form_with_errors.save.assert_not_called()

        # def test_invalid_list_items_arent_saved(self):
        #     self.client.post('/lists/new', data={'text': ''})
        #     self.assertEqual(Item.objects.count(), 0)
        #     self.assertEqual(List.objects.count(), 0)


class MyListsTest(unittest.TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.logged_in_user = User(email='frank@example.com')
        self.request.user = self.logged_in_user

    @patch('lists.views.render')
    def test_renders_the_my_lists_template(self, mock_render):
        response = my_lists(self.request)

        mock_render.assert_called_once()
        ((request, template_used, __), ___) = mock_render.call_args
        self.assertEqual(response, mock_render.return_value)
        self.assertEqual(template_used, 'my_lists.html')
        self.assertEqual(request, self.request)

    @patch('lists.views.render')
    def test_pass_the_logged_in_user_to_template(self, mock_render):
        response = my_lists(self.request)

        ((_, __, context), ___) = mock_render.call_args
        self.assertEqual(context['owner'], self.logged_in_user)
