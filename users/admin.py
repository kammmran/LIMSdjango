from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['name']
    search_fields = ['name', 'description']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'role']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('LIMS Information', {'fields': ('role', 'phone', 'department', 'employee_id')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('LIMS Information', {'fields': ('role', 'phone', 'department', 'employee_id')}),
    )
