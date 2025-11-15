from django import forms
from .models import Sample, SampleAttachment


class SampleForm(forms.ModelForm):
    """Form for creating/editing samples."""
    class Meta:
        model = Sample
        fields = ['sample_type', 'source', 'priority', 'notes', 'assigned_technician']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


class SampleAttachmentForm(forms.ModelForm):
    """Form for uploading sample attachments."""
    class Meta:
        model = SampleAttachment
        fields = ['file', 'description']
