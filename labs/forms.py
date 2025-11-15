from django import forms
from .models import Lab, Person, ResearchProject, Task, ProjectAttachment, Source


class LabForm(forms.ModelForm):
    """Form for creating/editing labs"""
    
    class Meta:
        model = Lab
        fields = [
            'name', 'code', 'description', 'location',
            'head_of_lab', 'research_focus', 'established_date', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lab Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LAB-001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Building / Room'}),
            'head_of_lab': forms.Select(attrs={'class': 'form-control'}),
            'research_focus': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'established_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PersonForm(forms.ModelForm):
    """Form for creating/editing people"""
    
    class Meta:
        model = Person
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'position',
            'role', 'orcid', 'skills', 'lab', 'is_active', 'joined_date', 'photo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'orcid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000-0000-0000-0000'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Python, Machine Learning, etc.'}),
            'lab': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'joined_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ResearchProjectForm(forms.ModelForm):
    """Form for creating/editing research projects"""
    
    class Meta:
        model = ResearchProject
        fields = [
            'lab', 'title', 'summary', 'principal_investigator',
            'team_members', 'start_date', 'end_date', 'status',
            'priority', 'funding_source', 'budget', 'notes'
        ]
        widgets = {
            'lab': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'principal_investigator': forms.Select(attrs={'class': 'form-control'}),
            'team_members': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'funding_source': forms.TextInput(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TaskForm(forms.ModelForm):
    """Form for creating/editing tasks"""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'lab', 'project',
            'assigned_to', 'status', 'priority', 'deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lab': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ProjectAttachmentForm(forms.ModelForm):
    """Form for uploading project attachments"""
    
    class Meta:
        model = ProjectAttachment
        fields = ['title', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class SourceForm(forms.ModelForm):
    """Form for creating/editing sources (customers, patients, labs)"""
    
    class Meta:
        model = Source
        fields = [
            'source_type', 'name', 'code', 'email', 'phone',
            'address', 'city', 'state_province', 'postal_code', 'country',
            'organization_name', 'department',
            'date_of_birth', 'gender', 'patient_id',
            'lab_reference', 'accreditation',
            'contact_person', 'contact_title', 'contact_email', 'contact_phone',
            'billing_reference', 'notes', 'is_active'
        ]
        widgets = {
            'source_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_source_type'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name or organization'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SRC-001'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1-555-0000'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state_province': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'patient_id': forms.TextInput(attrs={'class': 'form-control'}),
            'lab_reference': forms.Select(attrs={'class': 'form-control'}),
            'accreditation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CAP, CLIA, ISO'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_title': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
