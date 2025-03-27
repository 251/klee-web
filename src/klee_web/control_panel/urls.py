from django.urls import path
from control_panel import example_manager, views

app_name = 'control_panel'

urlpatterns = [
    path('', views.index, name='index'),
    path('worker/list/', views.worker_list, name='worker_list'),
    path('worker/config/', views.worker_config, name='worker_config'),

    path('task/list/', views.task_list, name='task_list'),
    path('task/list/<str:type>/', views.task_list, name='task_list_filtered'),
    path('task/kill/', views.kill_task, name='kill_task'),

    path('job/history/', views.get_job_history, name='get_job_history'),

    # Project-related URLs
    path('project/', example_manager.ProjectListView.as_view(), name='example_project_list'),
    path('project/create/', example_manager.ProjectCreateView.as_view(), name='example_project_create'),
    path('project/<int:pk>/', example_manager.ProjectUpdateView.as_view(), name='example_project_update'),
    path('project/delete/<int:pk>/', example_manager.ProjectDeleteView.as_view(), name='example_project_delete'),

    # File-related URLs
    path('project/<int:project_pk>/file/', example_manager.FileCreateView.as_view(), name='example_file_create'),
    path('project/<int:project_pk>/file/<int:pk>/', example_manager.FileUpdateView.as_view(), name='example_file_update'),
    path('project/<int:project_pk>/file/<int:pk>/default/', example_manager.make_default_file, name='example_file_default'),
    path('project/<int:project_pk>/file/<int:pk>/delete/', example_manager.FileDeleteView.as_view(), name='example_file_delete'),
]
