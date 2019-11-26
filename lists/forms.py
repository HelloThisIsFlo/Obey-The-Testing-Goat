from django import forms
from django.core.exceptions import ValidationError
from lists.models import Item, List

EMPTY_ITEM_ERROR = "You can't have an empty list item"
DUPLICATE_ITEM_ERROR = "You've already got this in your list"


class ItemForm(forms.models.ModelForm):
    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-lg',
            })
        }
        error_messages = {
            'text': {'required': EMPTY_ITEM_ERROR}
        }


class NewItemWithExistingListForm(ItemForm):
    def __init__(self, list_=None, data=None):
        super().__init__(data=data)
        self.instance.list = list_

    def clean(self):
        is_duplicate = Item.objects.filter(
            list=self.instance.list, text=self.cleaned_data.get('text', '')
        ).exists()

        if is_duplicate:
            raise ValidationError({'text': DUPLICATE_ITEM_ERROR})

        return super().clean()


class NewListFromItemForm(ItemForm):
    def __init__(self, data=None, owner=None):
        super().__init__(data=data)
        self.owner = owner

    def save(self):
        text = self.cleaned_data['text']
        if self.owner:
            return List.create_new(first_item_text=text, owner=self.owner)
        else:
            return List.create_new(first_item_text=text)


class SharingForm(forms.Form):
    sharee = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'your-friend@example.com',
            'class': 'form-control input'
        }
    ))

    def __init__(self, list_id=None, data=None):
        self.list_id = list_id
        super().__init__(data=data)

    def save(self):
        list_ = List.objects.get(id=self.list_id)
        list_.add_sharee(email=self.cleaned_data['sharee'])
        return list_
