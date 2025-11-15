from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('', views.result_list, name='result_list'),
    path('enter/<int:assignment_id>/', views.enter_result, name='enter_result'),
    path('review/', views.review_results, name='review_results'),
    path('approve/<int:pk>/', views.approve_result, name='approve_result'),
    path('reject/<int:pk>/', views.reject_result, name='reject_result'),
    path('approved/', views.approved_results, name='approved_results'),
    path('export/<int:pk>/', views.export_result, name='export_result'),
]
