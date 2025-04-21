from django import forms
from django.forms import FileField

from .models import Document, Rectangle, Subtask

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['image','project']



class TextForm(forms.ModelForm):
    class Meta:
        model = Subtask
        fields = ['text'] #="__all__"



# https://docs.djangoproject.com/en/5.1/topics/http/file-uploads/
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class FileFieldForm(forms.ModelForm):

    Files = MultipleFileField()
    class Meta:
        model = Document
        fields = ['project']
    Archive_name = forms.CharField(required=True, max_length=255)


