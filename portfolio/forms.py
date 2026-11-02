from django import forms

from .models import PostComment


class CommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Add to the conversation. Use @username to tag someone.',
                    'maxlength': PostComment._meta.get_field('body').max_length,
                }
            ),
        }
