from django import forms
from .models import *

class UserPostForm(forms.ModelForm):

    title = forms.CharField(label="", widget=forms.TextInput(attrs={
        'placeholder':'Title',
    }))

    description = forms.CharField(label="", widget=forms.Textarea(attrs={
        'placeholder':'Description in detail...',
        'rows':'8',
        'cols':'80',
    }))

    class Meta:
        model = UserPost
        fields = ['title', 'description']

class AnswerForm(forms.ModelForm):

    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        'placeholder':'Write your answer...',
        'rows':'4',
        'cols':'80',
    }))

    class Meta:
        model = Answer
        fields = ['content',]