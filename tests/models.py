from django.db import models
from django.conf import settings
from samples.models import Sample


class Test(models.Model):
    """Test types available in the lab."""
    
    CATEGORY_CHOICES = [
        ('hematology', 'Hematology'),
        ('biochemistry', 'Biochemistry'),
        ('microbiology', 'Microbiology'),
        ('immunology', 'Immunology'),
        ('molecular', 'Molecular Biology'),
        ('pathology', 'Pathology'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    turnaround_time = models.IntegerField(help_text='Expected turnaround time in hours')
    
    # Cost Management
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                        help_text='Estimated cost per test')
    billable_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                         help_text='Amount charged to client')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        db_table = 'tests'
        ordering = ['name']


class TestParameter(models.Model):
    """Parameters for each test."""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='parameters')
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, blank=True)
    reference_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference_range_text = models.CharField(max_length=200, blank=True, 
                                            help_text='Text reference range (e.g., "Negative", "Positive")')
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.test.code} - {self.name}"
    
    class Meta:
        db_table = 'test_parameters'
        ordering = ['test', 'order', 'name']


class TestAssignment(models.Model):
    """Assignment of tests to samples."""
    
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('waiting_review', 'Waiting Review'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='test_assignments')
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='assigned')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='test_assignments'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tests'
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    started_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Time Management
    expected_completion = models.DateTimeField(null=True, blank=True,
                                              help_text='Expected completion based on turnaround time')
    deadline = models.DateTimeField(null=True, blank=True,
                                   help_text='Hard deadline for test completion')
    
    # Cost tracking
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     help_text='Actual cost incurred for this test')
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.sample.sample_id} - {self.test.code}"
    
    @property
    def is_overdue(self):
        """Check if test has passed its deadline."""
        if self.deadline:
            from django.utils import timezone
            now = timezone.now()
            return now > self.deadline and self.status not in ['completed']
        return False
    
    @property
    def is_deadline_approaching(self, hours=12):
        """Check if deadline is approaching within specified hours."""
        if self.deadline:
            from datetime import timedelta
            from django.utils import timezone
            now = timezone.now()
            threshold = now + timedelta(hours=hours)
            return now < self.deadline <= threshold and self.status not in ['completed']
        return False
    
    @property
    def time_remaining(self):
        """Calculate time remaining until deadline."""
        if self.deadline:
            from django.utils import timezone
            now = timezone.now()
            delta = self.deadline - now
            return delta
        return None
    
    def save(self, *args, **kwargs):
        """Auto-calculate expected completion if not provided."""
        if not self.expected_completion and self.test.turnaround_time:
            from datetime import timedelta
            from django.utils import timezone
            self.expected_completion = timezone.now() + timedelta(hours=self.test.turnaround_time)
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'test_assignments'
        ordering = ['-assigned_date']
        unique_together = ['sample', 'test']


class ReagentUsage(models.Model):
    """Track reagent usage for test assignments to calculate actual costs."""
    test_assignment = models.ForeignKey(TestAssignment, on_delete=models.CASCADE, related_name='reagent_usages')
    reagent = models.ForeignKey('inventory.Reagent', on_delete=models.CASCADE, related_name='test_usages')
    quantity_used = models.DecimalField(max_digits=10, decimal_places=4,
                                       help_text='Quantity of reagent used')
    unit_cost_at_usage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                            help_text='Cost per unit at time of usage')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    help_text='Total cost for this usage')
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    used_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.test_assignment} - {self.reagent.name} - {self.quantity_used}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate cost based on reagent unit cost."""
        if not self.unit_cost_at_usage and self.reagent.unit_cost:
            self.unit_cost_at_usage = self.reagent.unit_cost
        
        if self.unit_cost_at_usage and not self.total_cost:
            self.total_cost = self.quantity_used * self.unit_cost_at_usage
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'reagent_usages'
        ordering = ['-used_date']
