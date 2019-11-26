from django import forms
from django.core.exceptions import ValidationError
from lists.models import Item, List
from django.contrib.auth import get_user_model
User = get_user_model()

EMPTY_ITEM_ERROR = "You can't have an empty list item"
DUPLICATE_ITEM_ERROR = "You've already got this in your list"
USER_DOESNT_EXIST_ERROR = "This user doesn't exist"


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

    def __init__(self, list_=None, data=None):
        self.list_ = list_
        super().__init__(data=data)

    def clean(self):
        user_exists = User.exists(email=self.cleaned_data['sharee'])
        if not user_exists:
            raise ValidationError({'sharee': USER_DOESNT_EXIST_ERROR})
        return super().clean()

    def save(self):
        self.list_.add_sharee(email=self.cleaned_data['sharee'])
