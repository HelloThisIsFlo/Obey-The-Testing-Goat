from django import forms
from django.core.exceptions import ValidationError
from lists.models import Item, List

EMPTY_ITEM_ERROR = "You can't have an empty list item"
DUPLICATE_ITEM_ERROR = "You've already got this in your list"


class BaseItemForm(forms.models.ModelForm):
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


class ExistingListItemForm(BaseItemForm):
    def __init__(self, for_list, data=None):
        super().__init__(data=data)
        self.instance.list = for_list

    def clean(self):
        is_duplicate = Item.objects.filter(
            list=self.instance.list, text=self.cleaned_data.get('text', '')
        ).exists()

        if is_duplicate:
            raise ValidationError({'text': DUPLICATE_ITEM_ERROR})

        return super().clean()


class NewListForm(BaseItemForm):
    def __init__(self, owner=None, data=None):
        super().__init__(data=data)
        self.owner = owner

    def save(self):
        if self.owner.is_authenticated:
            return List.create_new(first_item_text=self.cleaned_data['text'], owner=self.owner)
        else:
            return List.create_new(first_item_text=self.cleaned_data['text'])
