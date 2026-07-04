from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Task
from .forms import TaskForm


class TaskListView(LoginRequiredMixin, ListView):
    model               = Task
    template_name       = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model         = Task
    form_class    = TaskForm
    template_name = 'tasks/task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model         = Task
    form_class    = TaskForm
    template_name = 'tasks/task_form.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model         = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url   = reverse_lazy('tasks:task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Task deleted.')
        return super().form_valid(form)


class TaskToggleView(LoginRequiredMixin, UpdateView):
    model  = Task
    fields = []                              # no fields — we update in code, not form
    success_url = reverse_lazy('tasks:task_list')

    def form_valid(self, form):
        task = form.instance
        # Toggle between done and todo
        task.status = 'done' if task.status != 'done' else 'todo'
        task.save()
        messages.success(self.request, 'Task status updated!')
        return super().form_valid(form)

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)