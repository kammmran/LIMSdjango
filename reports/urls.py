from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_dashboard, name='dashboard'),
    path('samples/', views.sample_report, name='sample_report'),
    path('tests/', views.test_report, name='test_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('instruments/', views.instrument_report, name='instrument_report'),
]
