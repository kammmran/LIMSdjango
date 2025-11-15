from django.urls import path
from . import views

app_name = 'samples'

urlpatterns = [
    path('', views.sample_list, name='sample_list'),
    path('register/', views.sample_create, name='sample_create'),
    path('<int:pk>/', views.sample_detail, name='sample_detail'),
    path('<int:pk>/edit/', views.sample_edit, name='sample_edit'),
    path('<int:pk>/delete/', views.sample_delete, name='sample_delete'),
]
