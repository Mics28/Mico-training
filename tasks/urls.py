from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Task URLs
    path('',                 views.TaskListView.as_view(),   name='task_list'),
    path('create/',          views.TaskCreateView.as_view(), name='task_create'),
    path('<int:pk>/edit/',   views.TaskUpdateView.as_view(), name='task_edit'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('<int:pk>/toggle/', views.TaskToggleView.as_view(), name='task_toggle'),

    # Category URLs
    path('categories/',                 views.CategoryListView.as_view(),   name='category_list'),
    path('categories/create/',          views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]