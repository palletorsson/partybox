from django.forms import ModelForm
from models import TextPost, ImagePost, Track
from django import forms

class TextForm(forms.Form):
    class Meta:
        model = TextPost
        fields = ('body')

class ImageForm(forms.Form):
    class Meta:
        model = ImagePost
        fields = ('body', 'imgfile')

class TrackForm(forms.Form):
    class Meta:
        model = Track
        fields = ('docfile')


