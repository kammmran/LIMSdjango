from django.db import models
from django.conf import settings


class Instrument(models.Model):
    """Laboratory instruments."""
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('calibration', 'Calibration Needed'),
        ('offline', 'Offline'),
    ]
    
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='operational')
    purchase_date = models.DateField(null=True, blank=True)
    last_calibration_date = models.DateField(null=True, blank=True)
    next_calibration_date = models.DateField(null=True, blank=True)
    calibration_frequency = models.IntegerField(help_text='Days between calibrations', default=365)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"
    
    class Meta:
        db_table = 'instruments'
        ordering = ['name']


class CalibrationRecord(models.Model):
    """Calibration records for instruments."""
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='calibrations')
    calibration_date = models.DateField()
    next_calibration_date = models.DateField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    standards_used = models.TextField()
    results = models.TextField()
    passed = models.BooleanField(default=True)
    certificate_file = models.FileField(upload_to='calibration_certificates/%Y/%m/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.instrument.name} - {self.calibration_date}"
    
    class Meta:
        db_table = 'calibration_records'
        ordering = ['-calibration_date']


class MaintenanceLog(models.Model):
    """Maintenance logs for instruments."""
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('emergency', 'Emergency'),
    ]
    
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=50, choices=MAINTENANCE_TYPE_CHOICES)
    maintenance_date = models.DateField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    parts_replaced = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    downtime_hours = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.instrument.name} - {self.maintenance_type} - {self.maintenance_date}"
    
    class Meta:
        db_table = 'maintenance_logs'
        ordering = ['-maintenance_date']
