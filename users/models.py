from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """User roles with permissions."""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('lab_manager', 'Lab Manager'),
        ('technician', 'Lab Technician'),
        ('reviewer', 'Results Reviewer'),
        ('viewer', 'Viewer'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    can_register_samples = models.BooleanField(default=False)
    can_assign_tests = models.BooleanField(default=False)
    can_enter_results = models.BooleanField(default=False)
    can_approve_results = models.BooleanField(default=False)
    can_manage_inventory = models.BooleanField(default=False)
    can_manage_instruments = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    can_manage_users = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        db_table = 'roles'
        ordering = ['name']


class User(AbstractUser):
    """Custom user model for LIMS."""
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def has_permission(self, permission):
        """Check if user has specific permission."""
        if self.is_superuser:
            return True
        if self.role:
            return getattr(self.role, permission, False)
        return False
    
    class Meta:
        db_table = 'users'
        ordering = ['username']
