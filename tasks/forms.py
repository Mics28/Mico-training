from django import forms
from .models import Task, Category


class TaskForm(forms.ModelForm):

    class Meta:
        model  = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'category']
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
            'priority': forms.Select(attrs={
                'class': 'form-control',
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type':  'date',        # renders as HTML5 date picker
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Only show THIS user's categories in the dropdown
            self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['category'].empty_label = 'No Category'
        self.fields['due_date'].required    = False
        self.fields['category'].required    = False


class CategoryForm(forms.ModelForm):

    class Meta:
        model  = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'e.g. Work, Personal, Study...',
            }),
        }