from django.test import TestCase
from django.core.exceptions import ValidationError

from lists.models import Item, List


class ItemModelTest(TestCase):
    def test_default_text(self):
        item = Item()
        self.assertEqual(item.text, '')


class ListModelTest(TestCase):
    def test_get_absolute_url(self):
        list_ = List.objects.create()
        self.assertEqual(list_.get_absolute_url(), f'/lists/{list_.id}/')


class ListAndItemModelTest(TestCase):
    def test_item_is_related_to_list(self):
        list_ = List.objects.create()
        item = Item()
        item.list = list_
        item.save()
        self.assertIn(item, list_.item_set.all())

    def test_cannot_validate_empty_list_item(self):
        list_ = List.objects.create()
        item = Item(list=list_, text='')
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_cannot_validate_duplicate_list_item(self):
        duplicate_text = 'some item'
        list_ = List.objects.create()
        Item.objects.create(list=list_, text=duplicate_text)

        duplicate_item = Item(list=list_, text=duplicate_text)
        with self.assertRaises(ValidationError):
            duplicate_item.full_clean()

    def test_can_save_same_item_to_different_lists(self):
        duplicate_text = 'some item'
        list_1 = List.objects.create()
        list_2 = List.objects.create()

        Item.objects.create(list=list_1, text=duplicate_text)

        # When creating an item with the same description,
        # but in `list_2`
        # No exception should be raised
        duplicate_item_in_different_list = Item(
            list=list_2, text=duplicate_text
        )
        duplicate_item_in_different_list.full_clean()

    def test_list_ordering(self):
        list_ = List.objects.create()
        item1 = Item.objects.create(list=list_, text='i1')
        item2 = Item.objects.create(list=list_, text='i2')
        item3 = Item.objects.create(list=list_, text='i3')
        self.assertEqual(
            list(Item.objects.all()),
            [item1, item2, item3]
        )

    def test_string_representation(self):
        item = Item(text='some text')
        self.assertEqual(str(item), 'some text')
