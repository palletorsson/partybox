
from django.forms import ModelForm
from models import Post
from django import forms


class PostForm(forms.Form):
    class Meta:
        model = Post
        fields = ('body', 'docfile')

