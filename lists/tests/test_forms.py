import unittest
from unittest.mock import patch, Mock
from unittest import skip
from django.test import TestCase
from lists.forms import EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR, ExistingListItemForm, NewListForm
from lists.models import List, Item


# My understanding of forms so far
# --------------------------------
#
# Forms are wrapper around Models that:
# - Perform automatic validation before saving
#   - Based on the Model constraints
#   - As opposed to calling 'save()' on the model itself
#     (without calling 'full_clean()' before)
# - Generate HTML & error message
#


class ExistingListItemFormTest(TestCase):
    def test_form_item_input_has_placeholder_and_css_classes(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg', form.as_p())

    def test_form_validation_for_blank_items(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': ''})

        with self.assertRaises(ValueError):
            form.save()

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [EMPTY_ITEM_ERROR]
        )

    def test_form_save_handles_saving_to_a_list(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': 'hello'})

        new_item = form.save()
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'hello')
        self.assertEqual(new_item.list, list_)

    def test_form_validation_for_duplicate_items(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='duplicate')

        form = ExistingListItemForm(for_list=list_, data={'text': 'duplicate'})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])


class NewListFormTest(unittest.TestCase):
    @skip("""
    This is an example of how to NOT write a test with Mocks, instead
    simplify the interface to test we have the one. . . we wish we had.
    """)
    @patch('lists.forms.List')
    @patch('lists.forms.Item')
    def test_save_creates_new_list_and_item_from_post_data(self, MockItem, MockList):
        mock_list = MockList()
        mock_item = MockItem()

        user = Mock()

        form = NewListForm(owner=user, data={'text': 'new item text'})
        form.is_valid()  # Call to populate 'cleaned_data'

        def assert_item_saved_with_correct_values():
            self.assertEqual(mock_item.text, 'new item text')
            self.assertEqual(mock_item.owner, user)
            self.assertEqual(mock_item.list, mock_list)
            mock_list.save.assert_called_once()
        mock_item.save.side_effect = assert_item_saved_with_correct_values

        form.save()
        mock_item.save.assert_called_once()

    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_from_post_data_if_user_not_authenticated(
        self, mock_List_create_new
    ):
        user = Mock(is_authenticated=False)
        form = NewListForm(owner=user, data={'text': 'new item text'})
        form.is_valid()
        form.save()
        mock_List_create_new.assert_called_once_with(
            first_item_text='new item text'
        )

    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_from_post_data_if_user_authenticated(
        self, mock_List_create_new
    ):
        user = Mock(is_authenticated=True)
        form = NewListForm(owner=user, data={'text': 'new item text'})
        form.is_valid()
        form.save()
        mock_List_create_new.assert_called_once_with(
            first_item_text='new item text',
            owner=user
        )

    @patch('lists.forms.List.create_new')
    def test_save_returns_new_list_object(
        self, mock_List_create_new
    ):
        user = Mock(is_authenticated=True)
        form = NewListForm(owner=user, data={'text': 'new item text'})
        form.is_valid()
        saved_list = form.save()
        self.assertEqual(saved_list, mock_List_create_new.return_value)
