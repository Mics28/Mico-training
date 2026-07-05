from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Task, Category
from .forms import TaskForm, CategoryForm


# ─────────────────────────────────────────
#  Task Views
# ─────────────────────────────────────────

class TaskListView(LoginRequiredMixin, ListView):
    model               = Task
    template_name       = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__id=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model         = Task
    form_class    = TaskForm
    template_name = 'tasks/task_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user       # pass user to form __init__
        return kwargs

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user       # pass user to form __init__
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model       = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Task deleted.')
        return super().form_valid(form)


class TaskToggleView(LoginRequiredMixin, UpdateView):
    model       = Task
    fields      = []
    success_url = reverse_lazy('tasks:task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def form_valid(self, form):
        task        = form.instance
        task.status = 'done' if task.status != 'done' else 'todo'
        task.save()
        messages.success(self.request, 'Task status updated!')
        return super().form_valid(form)


# ─────────────────────────────────────────
#  Category Views
# ─────────────────────────────────────────

class CategoryListView(LoginRequiredMixin, ListView):
    model               = Category
    template_name       = 'tasks/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CategoryForm()   # ← pass empty form on every GET
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model         = Category
    form_class    = CategoryForm
    template_name = 'tasks/category_list.html'
    success_url   = reverse_lazy('tasks:category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Category created!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Could not create category.')
        return super().form_invalid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model       = Category
    success_url = reverse_lazy('tasks:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # Skip confirmation page — delete directly from the category list
        return self.post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Category deleted.')
        return super().form_valid(form)