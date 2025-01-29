from django import forms
from .models import Document, Rectangle, Subtask

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['image','project']

class TextForm(forms.ModelForm):
    class Meta:
        model = Subtask
        fields = ['text'] #="__all__"