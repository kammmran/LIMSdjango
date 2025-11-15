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


class InstrumentBorrowing(models.Model):
    """Track instrument borrowing/lending with samples and custom items like lectures, etc."""
    
    BORROWER_TYPE_CHOICES = [
        ('internal_user', 'Internal User'),
        ('external_user', 'External User'),
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('researcher', 'Researcher'),
        ('lab', 'Laboratory'),
        ('department', 'Department'),
        ('other', 'Other'),
    ]
    
    PURPOSE_CHOICES = [
        ('research', 'Research'),
        ('teaching', 'Teaching/Lecture'),
        ('demonstration', 'Demonstration'),
        ('training', 'Training'),
        ('testing', 'Testing/Analysis'),
        ('calibration', 'Calibration'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('borrowed', 'Currently Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Instrument being borrowed
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='borrowing_records'
    )
    
    # Borrower Information
    borrower_type = models.CharField(max_length=20, choices=BORROWER_TYPE_CHOICES)
    borrower_name = models.CharField(max_length=200, help_text='Name of person/department borrowing')
    borrower_email = models.EmailField(blank=True)
    borrower_phone = models.CharField(max_length=20, blank=True)
    borrower_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrowed_instruments',
        help_text='Link to user account if internal user'
    )
    
    # Link to labs module if borrower is from labs
    borrower_lab = models.ForeignKey(
        'labs.Lab',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrowed_instruments',
        help_text='Lab borrowing the instrument'
    )
    borrower_person = models.ForeignKey(
        'labs.Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrowed_instruments',
        help_text='Person from labs module'
    )
    
    # Associated sample if borrowing for sample analysis
    sample = models.ForeignKey(
        'samples.Sample',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instrument_borrowings',
        help_text='Sample to be analyzed (if applicable)'
    )
    
    # Purpose and Details
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    purpose_description = models.TextField(
        help_text='Detailed description of intended use'
    )
    location_of_use = models.CharField(
        max_length=200,
        help_text='Where the instrument will be used'
    )
    
    # Time Tracking
    requested_date = models.DateTimeField(auto_now_add=True)
    requested_start_date = models.DateTimeField(help_text='When borrower needs the instrument')
    requested_end_date = models.DateTimeField(help_text='When borrower will return the instrument')
    
    actual_borrow_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When instrument was actually borrowed'
    )
    actual_return_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When instrument was actually returned'
    )
    
    # Duration calculations
    @property
    def requested_duration_hours(self):
        """Calculate requested duration in hours"""
        if self.requested_start_date and self.requested_end_date:
            delta = self.requested_end_date - self.requested_start_date
            return round(delta.total_seconds() / 3600, 1)
        return None
    
    @property
    def actual_duration_hours(self):
        """Calculate actual duration in hours"""
        if self.actual_borrow_date and self.actual_return_date:
            delta = self.actual_return_date - self.actual_borrow_date
            return round(delta.total_seconds() / 3600, 1)
        return None
    
    @property
    def borrower_display(self):
        """Get display name for borrower"""
        if self.borrower_person:
            return self.borrower_person.full_name
        elif self.borrower_lab:
            return self.borrower_lab.name
        elif self.borrower_user:
            return self.borrower_user.get_full_name() or self.borrower_user.username
        else:
            return self.borrower_name
    
    @property
    def is_overdue(self):
        """Check if borrowing is overdue"""
        from django.utils import timezone
        if self.status == 'borrowed' and self.requested_end_date:
            return timezone.now() > self.requested_end_date
        return False
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        from django.utils import timezone
        if self.is_overdue:
            delta = timezone.now() - self.requested_end_date
            return delta.days
        return 0
    
    # Status and Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_borrowings'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    
    # Condition tracking
    condition_at_checkout = models.TextField(
        blank=True,
        help_text='Condition of instrument when borrowed'
    )
    condition_at_return = models.TextField(
        blank=True,
        help_text='Condition of instrument when returned'
    )
    
    # Additional Information
    accessories_borrowed = models.TextField(
        blank=True,
        help_text='List of accessories borrowed with instrument'
    )
    special_instructions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_borrowings'
    )
    
    class Meta:
        db_table = 'instrument_borrowings'
        ordering = ['-requested_date']
        indexes = [
            models.Index(fields=['status', 'requested_start_date']),
            models.Index(fields=['instrument', 'status']),
        ]
    
    def __str__(self):
        return f"{self.instrument.name} - {self.borrower_name} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-update status to overdue if needed"""
        if self.is_overdue and self.status == 'borrowed':
            self.status = 'overdue'
        super().save(*args, **kwargs)
