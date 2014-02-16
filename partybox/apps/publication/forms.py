
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('body',)
