from django.urls import path
from . import views

app_name = 'instruments'

urlpatterns = [
    path('', views.instrument_list, name='instrument_list'),
    path('create/', views.instrument_create, name='instrument_create'),
    path('<int:pk>/edit/', views.instrument_edit, name='instrument_edit'),
    path('<int:pk>/', views.instrument_detail, name='instrument_detail'),
    path('calibration/', views.calibration_list, name='calibration_list'),
    path('calibration/add/<int:instrument_id>/', views.calibration_add, name='calibration_add'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/add/<int:instrument_id>/', views.maintenance_add, name='maintenance_add'),
]
