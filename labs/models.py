from django.db import models
from django.conf import settings
from django.core.validators import EmailValidator
from django.urls import reverse


class Lab(models.Model):
    """Laboratory/Research Group"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Lab identifier code")
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    head_of_lab = models.ForeignKey(
        'Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='labs_headed'
    )
    research_focus = models.TextField(blank=True, help_text="Main research areas")
    established_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Laboratory'
        verbose_name_plural = 'Laboratories'

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_absolute_url(self):
        return reverse('labs:lab_detail', kwargs={'pk': self.pk})

    @property
    def member_count(self):
        return self.members.filter(is_active=True).count()

    @property
    def active_projects_count(self):
        return self.projects.filter(status='active').count()


class Person(models.Model):
    """Lab member/researcher"""
    ROLE_CHOICES = [
        ('lab_manager', 'Lab Manager'),
        ('researcher', 'Researcher'),
        ('assistant', 'Assistant'),
        ('student', 'Student'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='researcher')
    orcid = models.CharField(max_length=50, blank=True, help_text="ORCID identifier")
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    lab = models.ForeignKey(
        Lab,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='person_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Person'
        verbose_name_plural = 'People'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('labs:person_detail', kwargs={'pk': self.pk})


class ResearchProject(models.Model):
    """Research project within a lab"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=300)
    summary = models.TextField(blank=True)
    principal_investigator = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects_led'
    )
    team_members = models.ManyToManyField(Person, related_name='projects', blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    funding_source = models.CharField(max_length=200, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', 'title']
        verbose_name = 'Research Project'
        verbose_name_plural = 'Research Projects'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('labs:project_detail', kwargs={'pk': self.pk})

    @property
    def is_overdue(self):
        if self.end_date and self.status == 'active':
            from datetime import date
            return date.today() > self.end_date
        return False


class ProjectAttachment(models.Model):
    """Attachments for research projects"""
    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='project_attachments/%Y/%m/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class Task(models.Model):
    """Task management for labs and projects"""
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lab = models.ForeignKey(
        Lab,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )
    assigned_to = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'deadline', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.deadline and self.status != 'done':
            from datetime import date
            return date.today() > self.deadline
        return False

    def get_absolute_url(self):
        return reverse('labs:task_detail', kwargs={'pk': self.pk})


class Source(models.Model):
    """
    External entity that can be a sample source (Customer, Patient, External Lab, etc.)
    Manages relationships with samples and enables inter-lab collaboration
    """
    SOURCE_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('patient', 'Patient'),
        ('external_lab', 'External Laboratory'),
        ('internal_lab', 'Internal Laboratory'),
        ('research_partner', 'Research Partner'),
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    name = models.CharField(max_length=200, help_text="Full name or organization name")
    code = models.CharField(max_length=50, unique=True, help_text="Unique identifier code")
    
    # Contact Information
    email = models.EmailField(blank=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True, verbose_name="State/Province")
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Organization Details (for labs, hospitals, etc.)
    organization_name = models.CharField(max_length=200, blank=True, 
                                        help_text="Parent organization if applicable")
    department = models.CharField(max_length=200, blank=True)
    
    # Patient-specific fields
    date_of_birth = models.DateField(null=True, blank=True, help_text="For patient sources only")
    gender = models.CharField(max_length=20, blank=True, 
                             choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('U', 'Unknown')])
    patient_id = models.CharField(max_length=100, blank=True, unique=True, null=True,
                                 help_text="External patient ID")
    
    # Lab-specific fields (for inter-lab transfers)
    lab_reference = models.ForeignKey(
        Lab,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='external_sources',
        help_text="Link to internal lab if source is an internal laboratory"
    )
    accreditation = models.CharField(max_length=200, blank=True, 
                                    help_text="CAP, CLIA, ISO certifications, etc.")
    
    # Contact Person
    contact_person = models.CharField(max_length=200, blank=True)
    contact_title = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True, help_text="Additional notes or special instructions")
    billing_reference = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_sources'
    )
    
    class Meta:
        ordering = ['name', 'code']
        verbose_name = 'Source'
        verbose_name_plural = 'Sources'
        indexes = [
            models.Index(fields=['source_type', 'is_active']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"
    
    def get_absolute_url(self):
        return reverse('labs:source_detail', kwargs={'pk': self.pk})
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [
            self.address,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ', '.join([p for p in parts if p])
    
    @property
    def display_name(self):
        """Return display name based on source type"""
        if self.source_type == 'patient' and self.patient_id:
            return f"{self.name} (ID: {self.patient_id})"
        elif self.source_type in ['external_lab', 'internal_lab'] and self.organization_name:
            return f"{self.organization_name} - {self.name}"
        return self.name
    
    def can_send_samples_to_lab(self, lab):
        """Check if this source can send samples to the specified lab"""
        # Internal labs can send to any lab
        if self.source_type == 'internal_lab' and self.lab_reference:
            return True
        # External labs need to be active
        if self.source_type == 'external_lab':
            return self.is_active
        # Other sources can send if active
        return self.is_active
    
    @property
    def sample_count(self):
        """Count of samples from this source"""
        return self.samples.count()
