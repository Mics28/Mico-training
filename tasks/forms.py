from django import forms
from .models import Task


class TaskForm(forms.ModelForm):

    class Meta:
        model  = Task
        fields = ['title', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Enter task title...',
            }),
            'description': forms.Textarea(attrs={
                'class':       'form-control',
                'placeholder': 'Describe the task (optional)...',
                'rows':        4,
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
        }