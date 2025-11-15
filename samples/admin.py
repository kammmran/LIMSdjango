from django.contrib import admin
from .models import Sample, SampleAttachment


class SampleAttachmentInline(admin.TabularInline):
    model = SampleAttachment
    extra = 0
    readonly_fields = ['uploaded_by', 'uploaded_at']


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ['sample_id', 'sample_type', 'source', 'status', 'priority', 
                    'assigned_technician', 'received_date', 'completion_deadline', 'is_overdue']
    list_filter = ['status', 'sample_type', 'priority', 'received_date']
    search_fields = ['sample_id', 'source']
    readonly_fields = ['sample_id', 'registered_by', 'created_at', 'updated_at', 'is_overdue', 'days_until_deadline']
    inlines = [SampleAttachmentInline]
    
    fieldsets = (
        ('Sample Information', {
            'fields': ('sample_id', 'sample_type', 'source', 'status', 'priority')
        }),
        ('Time Management', {
            'fields': ('expected_completion_date', 'completion_deadline', 'actual_completion_date',
                      'is_overdue', 'days_until_deadline')
        }),
        ('Assignment', {
            'fields': ('assigned_technician', 'registered_by')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SampleAttachment)
class SampleAttachmentAdmin(admin.ModelAdmin):
    list_display = ['sample', 'filename', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['sample__sample_id', 'filename']
    readonly_fields = ['uploaded_by', 'uploaded_at']
