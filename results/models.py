from django.db import models
from django.conf import settings
from tests.models import TestAssignment, TestParameter


class TestResult(models.Model):
    """Test results for test assignments."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    test_assignment = models.OneToOneField(
        TestAssignment,
        on_delete=models.CASCADE,
        related_name='result'
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='entered_results'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_results'
    )
    entered_date = models.DateTimeField(auto_now_add=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    reviewer_comments = models.TextField(blank=True)
    instrument_file = models.FileField(upload_to='instrument_files/%Y/%m/%d/', blank=True, null=True)
    
    def __str__(self):
        return f"Result for {self.test_assignment}"
    
    class Meta:
        db_table = 'test_results'
        ordering = ['-entered_date']


class ParameterResult(models.Model):
    """Individual parameter results."""
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='parameter_results')
    parameter = models.ForeignKey(TestParameter, on_delete=models.CASCADE)
    value_numeric = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    value_text = models.CharField(max_length=500, blank=True)
    is_abnormal = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.parameter.name}: {self.value_numeric or self.value_text}"
    
    def check_abnormal(self):
        """Check if result is outside reference range."""
        if self.value_numeric and self.parameter.reference_range_min and self.parameter.reference_range_max:
            if self.value_numeric < self.parameter.reference_range_min or \
               self.value_numeric > self.parameter.reference_range_max:
                self.is_abnormal = True
            else:
                self.is_abnormal = False
    
    class Meta:
        db_table = 'parameter_results'
        ordering = ['parameter__order', 'parameter__name']
