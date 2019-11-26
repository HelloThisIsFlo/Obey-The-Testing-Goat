from unittest.mock import patch, ANY
import unittest
from lists.forms import NewItemWithExistingListForm, EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR, NewListFromItemForm, SharingForm
from lists.models import Item, List
from lists.views import home_page, my_lists, new_list, view_list
from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest, Http404
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
User = get_user_model()


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_uses_new_list_from_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], NewListFromItemForm)


class ListViewIntegratedTest(TestCase):
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
        self.assertIsInstance(
            response.context['form'], NewItemWithExistingListForm)

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
        self.assertIsInstance(
            response.context['form'], NewItemWithExistingListForm)
        self.assertContains(response, 'name="text"')

    def test_displays_sharing_form(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['sharing_form'], SharingForm)
        self.assertContains(response, 'name="sharee"')

    def test_raise_404_when_user_not_logged_in_and_list_not_public(self):
        owner = User.objects.create(email='a@b.com')
        list_ = List.create_new(first_item_text='First list item', owner=owner)

        response = self.client.get(list_.get_absolute_url(), follow=True)

        self.assertContains(response, 'Page not found', status_code=404)

    def test_logged_in_user_can_access_her_lists(self):
        owner = User.objects.create(email='a@b.com')
        list_ = List.create_new(first_item_text='First list item', owner=owner)
        self.client.force_login(owner)

        response = self.client.get(list_.get_absolute_url(), follow=True)

        self.assertContains(response, 'First list item', status_code=200)

    def test_logged_in_user_can_access_lists_shared_with_her(self):
        owner = User.objects.create(email='a@b.com')
        edith = User.objects.create(email='edith@b.com')
        list_ = List.create_new(first_item_text='First list item', owner=owner)
        list_.add_sharee(email='edith@b.com')
        self.client.force_login(edith)

        response = self.client.get(list_.get_absolute_url(), follow=True)

        self.assertContains(response, 'First list item', status_code=200)


@patch('lists.views.List')
@patch('lists.views.SharingForm')
@patch('lists.views.redirect')
@patch('lists.views.render')
class ListViewSharingTest(unittest.TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.request.user = AnonymousUser()

    def test_after_share_POST_get_list_with_id(self, mock_render, mock_redirect, MockSharingForm, MockList):
        list_ = MockList.objects.get.return_value
        list_.owner = None
        list_id = 1234
        self.request.POST['sharee'] = 'a@b.com'

        response = view_list(self.request, list_id)

        MockList.objects.get.assert_called_once_with(id=list_id)

    def test_after_share_POST_call_is_valid_and_then_saves_the_form(self, mock_render, mock_redirect, MockSharingForm, MockList):
        def assert_is_valid_was_called():
            form.is_valid.assert_called_once()

        form = MockSharingForm.return_value
        list_ = MockList.objects.get.return_value
        list_.owner = None
        list_id = 1234
        self.request.POST['sharee'] = 'a@b.com'
        form.save.side_effect = assert_is_valid_was_called

        response = view_list(self.request, list_id)

        MockSharingForm.assert_called_once_with(
            list_=MockList.objects.get.return_value,
            data=self.request.POST
        )
        form.save.assert_called_once()

    def test_after_share_POST_redirects_to_list(self, mock_render, mock_redirect, MockSharingForm, MockList):
        list_ = MockList.objects.get.return_value
        list_.owner = None
        list_id = 1234
        self.request.POST['sharee'] = 'a@b.com'

        response = view_list(self.request, list_id)

        form = MockSharingForm.return_value
        mock_redirect.assert_called_once_with(list_)
        self.assertEqual(response, mock_redirect.return_value)

    def test_after_share_POST_invalid_render_list_view_with_sharing_form_with_erros(self, mock_render, mock_redirect, MockSharingForm, MockList):
        form = MockSharingForm.return_value
        list_ = MockList.objects.get.return_value
        list_.owner = None
        list_id = 1234
        self.request.POST['sharee'] = 'a@b.com'

        form.is_valid.return_value = False
        response = view_list(self.request, list_id)

        MockSharingForm.assert_called_once_with(
            list_=MockList.objects.get.return_value,
            data=self.request.POST
        )
        mock_render.assert_called_once()
        ((_, __, context), ___) = mock_render.call_args
        self.assertEqual(context['sharing_form'], form)
        self.assertEqual(response, mock_render.return_value)


class ListViewSharingIntegratedTest(TestCase):
    def test_add_sharee(self):
        edith = User.objects.create(email='edith@example.com')
        frank = User.objects.create(email='frank@example.com')

        list_ = List.create_new(first_item_text="Edith's list", owner=edith)

        self.client.force_login(edith)
        self.client.post(
            f'/lists/{list_.id}/',
            {'sharee': 'frank@example.com'}
        )

        saved_list = List.objects.first()
        self.assertEqual(saved_list.sharees.first(), frank)


@patch('lists.views.NewListFromItemForm')
class NewListTest(unittest.TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.user = AnonymousUser()
        self.request.POST['text'] = 'some text'

    def test_can_save_a_POST_request(self, MockNewListFromItemForm):
        new_list(self.request)

        MockNewListFromItemForm.assert_called_once_with(data=self.request.POST)
        form = MockNewListFromItemForm()
        form.save.assert_called_once()

    def test_saves_current_user_as_owner_if_authenticated(self, MockNewListFromItemForm):
        logged_in_user = User(email='a@b.com')
        self.request.user = logged_in_user

        new_list(self.request)

        MockNewListFromItemForm.assert_called_once_with(
            data=self.request.POST, owner=logged_in_user)
        form = MockNewListFromItemForm()
        form.save.assert_called_once()

    @patch('lists.views.redirect')
    def test_redirects_after_POST(self, mock_redirect, MockNewListFromItemForm):
        form = MockNewListFromItemForm()

        response = new_list(self.request)

        saved_list = form.save.return_value
        mock_redirect.assert_called_once_with(saved_list)
        self.assertEqual(response, mock_redirect.return_value)

    @patch('lists.views.render')
    def test_for_invalid_input_renders_home_template_with_form_containing_errors(
        self,
        mock_render,
        MockNewListFromItemForm
    ):
        form = MockNewListFromItemForm()
        form.is_valid.return_value = False

        response = new_list(self.request)

        mock_render.assert_called_once_with(
            self.request,
            'home.html',
            {'form': form}
        )
        self.assertEqual(response, mock_render.return_value)

    @patch('lists.views.render')
    def test_invalid_list_items_arent_saved(
        self,
        mock_render,
        MockNewListFromItemForm
    ):
        form = MockNewListFromItemForm()
        form.is_valid.return_value = False

        response = new_list(self.request)

        form.save.assert_not_called()


class NewListIntegratedTest(TestCase):
    def test_can_save_a_POST_request(self):
        response = self.client.post(
            '/lists/new',
            data={'text': 'A new list item'}
        )
        self.assertEqual(List.objects.count(), 1)
        new_list = List.objects.first()
        self.assertEqual(new_list.item_set.first().text, 'A new list item')

    def test_validation_errors_are_show_on_home_page(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))


@patch('lists.views.render')
@patch('lists.views.User')
class MyListsTest(unittest.TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.user = User(email='a@b.com')

    def test_renders_my_lists_template(self, MockUserClass, mock_render):
        response = my_lists(self.request, 'a@b.com')
        mock_render.assert_called_once_with(self.request, 'my_lists.html', ANY)
        self.assertEqual(response, mock_render.return_value)

    def test_renders_with_correct_owner(self, MockUserClass, mock_render):
        response = my_lists(self.request, 'a@b.com')

        MockUserClass.objects.get.assert_called_once_with(email='a@b.com')
        ((_, _, context), __) = mock_render.call_args
        self.assertEqual(
            context['owner'],
            MockUserClass.objects.get.return_value
        )

    def test_raise_404_when_user_not_logged_in(self, MockUserClass, mock_render):
        self.request.user = AnonymousUser()

        with self.assertRaises(Http404):
            my_lists(self.request, 'a@b.com')

    def test_raise_404_when_logged_in_user_is_not_owner(self, MockUserClass, mock_render):
        self.request.user = User('not_owner@example.com')

        with self.assertRaises(Http404):
            my_lists(self.request, 'owner@example.com')


class MyListsIntegratedTest(TestCase):
    def test_shows_all_of_users_lists(self):
        User.objects.create(email='not_owner@b.com')
        user = User.objects.create(email='owner@b.com')
        List.create_new(
            first_item_text='First item from first list',
            owner=user
        )
        List.create_new(
            first_item_text='First item from second list',
            owner=user
        )

        self.client.force_login(user)
        response = self.client.get('/lists/users/owner@b.com/')

        self.assertContains(response, 'First item from first list')
        self.assertContains(response, 'First item from second list')
