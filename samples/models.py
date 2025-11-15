from django.db import models
from django.conf import settings


class Sample(models.Model):
    """Sample model for tracking laboratory samples."""
    
    SAMPLE_TYPE_CHOICES = [
        ('blood', 'Blood'),
        ('urine', 'Urine'),
        ('tissue', 'Tissue'),
        ('water', 'Water'),
        ('soil', 'Soil'),
        ('food', 'Food'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    sample_id = models.CharField(max_length=50, unique=True, db_index=True)
    sample_type = models.CharField(max_length=50, choices=SAMPLE_TYPE_CHOICES)
    source = models.CharField(max_length=200, help_text='Source/Customer/Patient')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='registered')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    received_date = models.DateField(auto_now_add=True)
    received_time = models.TimeField(auto_now_add=True)
    
    # Time Management fields
    expected_completion_date = models.DateField(null=True, blank=True,
                                                help_text='Expected completion deadline')
    completion_deadline = models.DateTimeField(null=True, blank=True,
                                               help_text='Hard deadline for completion')
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    assigned_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_samples'
    )
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registered_samples'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.sample_id} - {self.get_sample_type_display()}"
    
    @property
    def is_overdue(self):
        """Check if sample has passed its deadline."""
        if self.completion_deadline:
            from datetime import datetime
            from django.utils import timezone
            now = timezone.now()
            return now > self.completion_deadline and self.status not in ['completed', 'archived']
        return False
    
    @property
    def is_deadline_approaching(self, hours=24):
        """Check if deadline is approaching within specified hours."""
        if self.completion_deadline:
            from datetime import timedelta
            from django.utils import timezone
            now = timezone.now()
            threshold = now + timedelta(hours=hours)
            return now < self.completion_deadline <= threshold and self.status not in ['completed', 'archived']
        return False
    
    @property
    def days_until_deadline(self):
        """Calculate days remaining until deadline."""
        if self.completion_deadline:
            from django.utils import timezone
            now = timezone.now()
            delta = self.completion_deadline - now
            return delta.days
        return None
    
    def save(self, *args, **kwargs):
        """Auto-generate sample ID if not provided."""
        if not self.sample_id:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_sample = Sample.objects.filter(
                sample_id__startswith=f'SMP-{date_str}'
            ).order_by('-sample_id').first()
            
            if last_sample:
                last_num = int(last_sample.sample_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.sample_id = f'SMP-{date_str}-{new_num:04d}'
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'samples'
        ordering = ['-received_date', '-received_time']


class SampleAttachment(models.Model):
    """Attachments for samples."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='sample_attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sample.sample_id} - {self.filename}"
    
    class Meta:
        db_table = 'sample_attachments'
        ordering = ['-uploaded_at']
