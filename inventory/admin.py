from django.contrib import admin
from .models import Reagent, StockItem, InventoryTransaction, CostCenter, CostAllocation


@admin.register(Reagent)
class ReagentAdmin(admin.ModelAdmin):
    list_display = ['name', 'catalog_number', 'manufacturer', 'quantity', 'unit', 'unit_cost', 
                   'total_value', 'expiry_date', 'is_low_stock']
    list_filter = ['manufacturer', 'expiry_date', 'supplier']
    search_fields = ['name', 'catalog_number', 'manufacturer', 'supplier']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'catalog_number', 'manufacturer', 'lot_number')
        }),
        ('Inventory', {
            'fields': ('quantity', 'unit', 'minimum_quantity', 'storage_location')
        }),
        ('Cost Management', {
            'fields': ('unit_cost', 'currency', 'purchase_date', 'supplier')
        }),
        ('Safety & Expiry', {
            'fields': ('expiry_date', 'hazard_class')
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
    )


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'item_code', 'category', 'quantity', 'unit', 'cost_per_unit', 
                   'total_value', 'is_low_stock']
    list_filter = ['category', 'supplier']
    search_fields = ['name', 'item_code', 'supplier']


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'reagent', 'stock_item', 'quantity', 'unit_cost', 
                   'total_cost', 'performed_by', 'transaction_date']
    list_filter = ['transaction_type', 'transaction_date']
    readonly_fields = ['performed_by', 'transaction_date']


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'monthly_budget', 'yearly_budget', 'manager', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(CostAllocation)
class CostAllocationAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'cost_center', 'allocated_cost', 'percentage', 'created_at']
    list_filter = ['cost_center', 'created_at']
    readonly_fields = ['created_at']
