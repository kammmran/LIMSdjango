from django.contrib import admin
from .models import Lab, Person, ResearchProject, Task, ProjectAttachment, Source


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'location', 'head_of_lab', 'is_active', 'created_at']
    list_filter = ['is_active', 'established_date']
    search_fields = ['name', 'code', 'location', 'research_focus']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'location')
        }),
        ('Management', {
            'fields': ('head_of_lab', 'research_focus', 'established_date', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'role', 'lab', 'position', 'is_active']
    list_filter = ['role', 'is_active', 'lab']
    search_fields = ['first_name', 'last_name', 'email', 'orcid']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'photo')
        }),
        ('Professional Details', {
            'fields': ('position', 'role', 'orcid', 'skills', 'lab')
        }),
        ('Status', {
            'fields': ('is_active', 'joined_date')
        }),
        ('System', {
            'fields': ('user', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'lab', 'principal_investigator', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'priority', 'lab', 'start_date']
    search_fields = ['title', 'summary', 'funding_source']
    filter_horizontal = ['team_members']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Project Details', {
            'fields': ('lab', 'title', 'summary')
        }),
        ('Team', {
            'fields': ('principal_investigator', 'team_members')
        }),
        ('Timeline & Status', {
            'fields': ('start_date', 'end_date', 'status', 'priority')
        }),
        ('Funding', {
            'fields': ('funding_source', 'budget')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'lab', 'project', 'assigned_to', 'status', 'priority', 'deadline']
    list_filter = ['status', 'priority', 'lab', 'deadline']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description')
        }),
        ('Assignment', {
            'fields': ('lab', 'project', 'assigned_to', 'created_by')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'deadline', 'completed_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectAttachment)
class ProjectAttachmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['title', 'description', 'project__title']
    readonly_fields = ['uploaded_at']


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'source_type', 'email', 'phone', 'is_active', 'sample_count']
    list_filter = ['source_type', 'is_active', 'country', 'created_at']
    search_fields = ['name', 'code', 'email', 'organization_name', 'patient_id', 'contact_person']
    readonly_fields = ['created_at', 'updated_at', 'sample_count']
    autocomplete_fields = ['lab_reference', 'created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('source_type', 'name', 'code', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'city', 'state_province', 'postal_code', 'country')
        }),
        ('Organization Details', {
            'fields': ('organization_name', 'department', 'contact_person', 'contact_title', 
                      'contact_email', 'contact_phone'),
            'classes': ('collapse',)
        }),
        ('Patient Information', {
            'fields': ('patient_id', 'date_of_birth', 'gender'),
            'classes': ('collapse',),
            'description': 'For patient sources only'
        }),
        ('Lab Details', {
            'fields': ('lab_reference', 'accreditation'),
            'classes': ('collapse',),
            'description': 'For laboratory sources'
        }),
        ('Additional', {
            'fields': ('billing_reference', 'notes', 'created_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def sample_count(self, obj):
        return obj.sample_count
    sample_count.short_description = 'Samples'
