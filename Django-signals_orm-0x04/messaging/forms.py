from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()


class ReplyForm(forms.ModelForm):
    """Formulaire pour répondre à un message."""
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type your reply here...'
            }),
        }

class DeleteAccountForm(forms.Form):
    """
    Simple confirmation form for account deletion.
    """
    confirm = forms.BooleanField(
        required=True,
        label="I understand that this action cannot be undone.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('confirm'):
            raise forms.ValidationError("You must confirm that you want to delete your account.")
        return cleaned_data
