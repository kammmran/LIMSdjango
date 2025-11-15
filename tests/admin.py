from django.contrib import admin
from .models import Test, TestParameter, TestAssignment, ReagentUsage


class TestParameterInline(admin.TabularInline):
    model = TestParameter
    extra = 1


class ReagentUsageInline(admin.TabularInline):
    model = ReagentUsage
    extra = 0
    readonly_fields = ['used_by', 'used_date', 'total_cost']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'turnaround_time', 'estimated_cost', 
                   'billable_amount', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'code']
    inlines = [TestParameterInline]
    fieldsets = (
        ('Test Information', {
            'fields': ('code', 'name', 'category', 'description', 'is_active')
        }),
        ('Time Management', {
            'fields': ('turnaround_time',)
        }),
        ('Cost Management', {
            'fields': ('estimated_cost', 'billable_amount')
        }),
    )


@admin.register(TestAssignment)
class TestAssignmentAdmin(admin.ModelAdmin):
    list_display = ['sample', 'test', 'status', 'assigned_to', 'assigned_date', 'deadline', 
                   'actual_cost', 'is_overdue']
    list_filter = ['status', 'assigned_date']
    search_fields = ['sample__sample_id', 'test__name']
    readonly_fields = ['assigned_by', 'assigned_date', 'started_date', 'completed_date', 
                      'is_overdue', 'time_remaining']
    inlines = [ReagentUsageInline]
    fieldsets = (
        ('Assignment Information', {
            'fields': ('sample', 'test', 'status', 'assigned_to', 'assigned_by')
        }),
        ('Time Management', {
            'fields': ('assigned_date', 'started_date', 'completed_date', 
                      'expected_completion', 'deadline', 'is_overdue', 'time_remaining')
        }),
        ('Cost Tracking', {
            'fields': ('actual_cost',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(ReagentUsage)
class ReagentUsageAdmin(admin.ModelAdmin):
    list_display = ['test_assignment', 'reagent', 'quantity_used', 'unit_cost_at_usage', 
                   'total_cost', 'used_by', 'used_date']
    list_filter = ['used_date', 'reagent']
    search_fields = ['test_assignment__sample__sample_id', 'reagent__name']
    readonly_fields = ['used_by', 'used_date', 'total_cost']
