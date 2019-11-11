from django.test import TestCase
from django.core.exceptions import ValidationError

from lists.models import Item, List


class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_)

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

    def test_get_absolute_url(self):
        list_ = List.objects.create()
        self.assertEqual(list_.get_absolute_url(), f'/lists/{list_.id}/')

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
