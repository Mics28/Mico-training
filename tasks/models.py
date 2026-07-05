from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Task(models.Model):

    STATUS_CHOICES = [
        ('todo',        'To Do'),
        ('in_progress', 'In Progress'),
        ('done',        'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]

    # --- Existing Fields ---
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    # --- New Fields ---
    priority    = models.CharField(
                    max_length=10,
                    choices=PRIORITY_CHOICES,
                    default='medium'
                  )
    due_date    = models.DateField(null=True, blank=True)
    category    = models.ForeignKey(
                    Category,
                    on_delete=models.SET_NULL,
                    null=True,
                    blank=True,
                    related_name='tasks'
                  )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tasks:task_list')

    def is_done(self):
        return self.status == 'done'

    def is_overdue(self):
        from django.utils import timezone
        if self.due_date and not self.is_done():
            return self.due_date < timezone.now().date()
        return False

    def priority_order(self):
        order = {'high': 1, 'medium': 2, 'low': 3}
        return order.get(self.priority, 2)