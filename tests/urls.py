from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    path('', views.test_list, name='test_list'),
    path('types/', views.test_type_list, name='test_type_list'),
    path('types/create/', views.test_type_create, name='test_type_create'),
    path('types/<int:pk>/edit/', views.test_type_edit, name='test_type_edit'),
    path('assign/', views.assign_test, name='assign_test'),
    path('workflow/', views.test_workflow, name='test_workflow'),
    path('assignment/<int:pk>/update-status/', views.update_assignment_status, name='update_assignment_status'),
]
