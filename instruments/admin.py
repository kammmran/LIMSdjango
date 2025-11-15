from django.contrib import admin
from .models import Instrument, CalibrationRecord, MaintenanceLog, InstrumentBorrowing


class CalibrationRecordInline(admin.TabularInline):
    model = CalibrationRecord
    extra = 0
    readonly_fields = ['performed_by', 'created_at']


class MaintenanceLogInline(admin.TabularInline):
    model = MaintenanceLog
    extra = 0
    readonly_fields = ['performed_by', 'created_at']


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'model', 'serial_number', 'status', 'location', 'next_calibration_date']
    list_filter = ['status', 'manufacturer']
    search_fields = ['name', 'model', 'serial_number']
    inlines = [CalibrationRecordInline, MaintenanceLogInline]


@admin.register(CalibrationRecord)
class CalibrationRecordAdmin(admin.ModelAdmin):
    list_display = ['instrument', 'calibration_date', 'next_calibration_date', 'passed', 'performed_by']
    list_filter = ['passed', 'calibration_date']
    readonly_fields = ['performed_by', 'created_at']


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ['instrument', 'maintenance_type', 'maintenance_date', 'cost', 'performed_by']
    list_filter = ['maintenance_type', 'maintenance_date']
    readonly_fields = ['performed_by', 'created_at']


@admin.register(InstrumentBorrowing)
class InstrumentBorrowingAdmin(admin.ModelAdmin):
    list_display = ['instrument', 'borrower_name', 'borrower_type', 'status', 'requested_start_date', 'requested_end_date', 'actual_duration_hours']
    list_filter = ['status', 'borrower_type', 'purpose', 'requested_start_date']
    search_fields = ['borrower_name', 'borrower_email', 'instrument__name', 'purpose_description']
    readonly_fields = ['requested_date', 'created_at', 'updated_at', 'requested_duration_hours', 'actual_duration_hours', 'is_overdue', 'days_overdue']
    
    fieldsets = (
        ('Instrument', {
            'fields': ('instrument', 'status')
        }),
        ('Borrower Information', {
            'fields': ('borrower_type', 'borrower_name', 'borrower_email', 'borrower_phone', 
                      'borrower_user', 'borrower_lab', 'borrower_person')
        }),
        ('Purpose', {
            'fields': ('purpose', 'purpose_description', 'location_of_use', 'sample')
        }),
        ('Time Tracking', {
            'fields': ('requested_start_date', 'requested_end_date', 'requested_duration_hours',
                      'actual_borrow_date', 'actual_return_date', 'actual_duration_hours',
                      'is_overdue', 'days_overdue')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approval_date')
        }),
        ('Condition', {
            'fields': ('condition_at_checkout', 'condition_at_return', 'accessories_borrowed')
        }),
        ('Additional Info', {
            'fields': ('special_instructions', 'notes')
        }),
        ('Metadata', {
            'fields': ('requested_date', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
