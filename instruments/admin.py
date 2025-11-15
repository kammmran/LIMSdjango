from django.contrib import admin
from .models import Instrument, CalibrationRecord, MaintenanceLog


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
