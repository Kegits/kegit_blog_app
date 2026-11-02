from django import forms

from .models import DirectMessage


class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['body']
        widgets = {
            'body': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Write a private message…',
                    'maxlength': DirectMessage._meta.get_field('body').max_length,
                }
            ),
        }


class StartConversationForm(forms.Form):
    username = forms.CharField(max_length=150)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Enter their username',
                'autocomplete': 'off',
            }
        )
