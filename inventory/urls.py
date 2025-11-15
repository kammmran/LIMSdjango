from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_dashboard, name='dashboard'),
    path('reagents/', views.reagent_list, name='reagent_list'),
    path('reagents/create/', views.reagent_create, name='reagent_create'),
    path('reagents/<int:pk>/edit/', views.reagent_edit, name='reagent_edit'),
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/create/', views.stock_create, name='stock_create'),
    path('stock/<int:pk>/edit/', views.stock_edit, name='stock_edit'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('low-stock/', views.low_stock_alerts, name='low_stock_alerts'),
]
