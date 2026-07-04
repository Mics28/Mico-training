from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Task(models.Model):

    # Status choices — stored as short strings in DB, displayed as readable labels
    STATUS_CHOICES = [
        ('todo',        'To Do'),
        ('in_progress', 'In Progress'),
        ('done',        'Done'),
    ]

    # --- Columns / Fields ---
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']   # newest tasks appear first

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tasks:task_list')

    def is_done(self):
        return self.status == 'done'