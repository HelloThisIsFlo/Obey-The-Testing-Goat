from django.test import TestCase
from lists.forms import EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR, USER_DOESNT_EXIST_ERROR, NewItemWithExistingListForm, NewListFromItemForm, SharingForm
from lists.models import List, Item
import unittest
from unittest.mock import patch, MagicMock

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


class ItemFormTest(TestCase):
    def test_form_item_input_has_placeholder_and_css_classes(self):
        form = NewItemWithExistingListForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg', form.as_p())

    def test_form_validation_for_blank_items(self):
        list_ = List.objects.create()
        form = NewItemWithExistingListForm(list_=list_, data={'text': ''})

        with self.assertRaises(ValueError):
            form.save()

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [EMPTY_ITEM_ERROR]
        )

    def test_form_save_handles_saving_to_a_list(self):
        list_ = List.objects.create()
        form = NewItemWithExistingListForm(list_=list_, data={'text': 'hello'})

        new_item = form.save()
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'hello')
        self.assertEqual(new_item.list, list_)

    def test_form_validation_for_duplicate_items(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='duplicate')

        form = NewItemWithExistingListForm(
            list_=list_, data={'text': 'duplicate'})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])


class NewListFromItemFormTest(unittest.TestCase):
    def test_form_item_input_has_placeholder_and_css_classes(self):
        form = NewListFromItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg', form.as_p())

    @patch('lists.forms.List')
    def test_saves_new_list_with_item(self, MockList):
        form = NewListFromItemForm(data={'text': 'New item text'})

        form.is_valid()  # Populate 'cleaned_data'
        saved_list = form.save()

        MockList.create_new.assert_called_once_with(
            first_item_text='New item text')
        self.assertEqual(saved_list, MockList.create_new.return_value)

    @patch('lists.forms.List')
    def test_saves_new_list_with_item_and_owner(self, MockList):
        user = MagicMock()
        form = NewListFromItemForm(owner=user, data={'text': 'New item text'})

        form.is_valid()  # Populate 'cleaned_data'
        saved_list = form.save()

        MockList.create_new.assert_called_once_with(
            first_item_text='New item text',
            owner=user
        )
        self.assertEqual(saved_list, MockList.create_new.return_value)

    def test_valid_items_are_valid(self):
        form = NewListFromItemForm(data={'text': 'valid item'})
        self.assertTrue(form.is_valid())

    def test_blank_items_are_not_valid(self):
        form = NewListFromItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())


@patch('lists.forms.User')
class SharingFormTest(unittest.TestCase):
    def test_form_item_input_has_placeholder_and_css_classes(self, MockUser):
        form = SharingForm()
        self.assertIn('placeholder="your-friend@example.com"', form.as_p())
        self.assertIn('class="form-control input', form.as_p())

    def test_adds_sharee_on_save(self, MockUser):
        list_ = MagicMock()

        form = SharingForm(list_=list_, data={'sharee': 'a@b.com'})

        form.is_valid()  # populate 'cleaned_data'
        form.save()

        list_.add_sharee.assert_called_once_with(email='a@b.com')

    def test_valid_form(self, MockUser):
        MockUser.exists.return_value = True

        form = SharingForm(list_=MagicMock(), data={'sharee': 'a@b.com'})

        self.assertTrue(form.is_valid())
        MockUser.exists.assert_called_once_with(email='a@b.com')

    def test_invalid_form__user_doesnt_exist(self, MockUser):
        MockUser.exists.return_value = False

        form = SharingForm(list_=MagicMock(), data={'sharee': 'a@b.com'})

        self.assertFalse(form.is_valid())
        MockUser.exists.assert_called_once_with(email='a@b.com')
        self.assertIn(USER_DOESNT_EXIST_ERROR, form['sharee'].errors)
