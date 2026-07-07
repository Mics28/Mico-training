from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Task, Category
from .forms import TaskForm, CategoryForm
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import datetime


# ─────────────────────────────────────────
#  Task Views
# ─────────────────────────────────────────

class TaskListView(LoginRequiredMixin, ListView):
    model               = Task
    template_name       = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)

         # ── Search ──────────────────────────────────────
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

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
        context['search_query'] = self.request.GET.get('q', '')
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
    
class DashboardView(LoginRequiredMixin, ListView):
    model               = Task
    template_name       = 'tasks/dashboard.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user     = self.request.user
        today    = timezone.now().date()
        all_tasks = Task.objects.filter(user=user)

        # ── Status counts ──────────────────────────────
        context['total_tasks']       = all_tasks.count()
        context['todo_count']        = all_tasks.filter(status='todo').count()
        context['in_progress_count'] = all_tasks.filter(status='in_progress').count()
        context['done_count']        = all_tasks.filter(status='done').count()

        # ── Priority counts ────────────────────────────
        context['high_count']   = all_tasks.filter(priority='high').count()
        context['medium_count'] = all_tasks.filter(priority='medium').count()
        context['low_count']    = all_tasks.filter(priority='low').count()

        # ── Completion rate ────────────────────────────
        total = all_tasks.count()
        context['completion_rate'] = (
            round((context['done_count'] / total) * 100)
            if total > 0 else 0
        )

        # ── Overdue tasks ──────────────────────────────
        context['overdue_tasks'] = all_tasks.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress']
        )

        # ── Due this week ──────────────────────────────
        week_end = today + datetime.timedelta(days=7)
        context['due_this_week'] = all_tasks.filter(
            due_date__gte=today,
            due_date__lte=week_end,
            status__in=['todo', 'in_progress']
        )

        # ── Category breakdown ─────────────────────────
        context['category_stats'] = (
            Category.objects
            .filter(user=user)
            .annotate(
                total=Count('tasks'),
                done=Count('tasks', filter=Q(tasks__status='done'))
            )
        )

        # ── Chart data (passed as plain numbers for JS) ─
        context['chart_status'] = [
            context['todo_count'],
            context['in_progress_count'],
            context['done_count'],
        ]
        context['chart_priority'] = [
            context['high_count'],
            context['medium_count'],
            context['low_count'],
        ]

        return context
    
class KanbanView(LoginRequiredMixin, ListView):
    model               = Task
    template_name       = 'tasks/kanban.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = self.get_queryset()

        # Split tasks into 3 buckets for the 3 columns
        context['todo_tasks']        = tasks.filter(status='todo')
        context['in_progress_tasks'] = tasks.filter(status='in_progress')
        context['done_tasks']        = tasks.filter(status='done')
        return context


class TaskUpdateStatusAjaxView(LoginRequiredMixin, View):

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, user=request.user)
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)

        data       = json.loads(request.body)
        new_status = data.get('status')

        valid_statuses = ['todo', 'in_progress', 'done']
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

        task.status = new_status
        task.save()

        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'new_status': task.status,
        })