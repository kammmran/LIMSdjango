from django.urls import path
from . import views

app_name = 'labs'

urlpatterns = [
    # Dashboard
    path('', views.labs_dashboard, name='dashboard'),
    
    # Labs
    path('labs/', views.lab_list, name='lab_list'),
    path('labs/create/', views.lab_create, name='lab_create'),
    path('labs/<int:pk>/', views.lab_detail, name='lab_detail'),
    path('labs/<int:pk>/update/', views.lab_update, name='lab_update'),
    path('labs/<int:pk>/delete/', views.lab_delete, name='lab_delete'),
    
    # People
    path('people/', views.person_list, name='person_list'),
    path('people/create/', views.person_create, name='person_create'),
    path('people/<int:pk>/', views.person_detail, name='person_detail'),
    path('people/<int:pk>/update/', views.person_update, name='person_update'),
    path('people/<int:pk>/delete/', views.person_delete, name='person_delete'),
    
    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/update/', views.project_update, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Attachments
    path('projects/<int:project_pk>/attachments/create/', views.attachment_create, name='attachment_create'),
    path('attachments/<int:pk>/delete/', views.attachment_delete, name='attachment_delete'),
    
    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/kanban/', views.task_kanban, name='task_kanban'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/update-status/', views.task_update_status, name='task_update_status'),
]
