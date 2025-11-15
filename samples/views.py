from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Sample, SampleAttachment
from .forms import SampleForm, SampleAttachmentForm


@login_required
def sample_list(request):
    """List all samples with filtering and pagination."""
    samples = Sample.objects.select_related('assigned_technician', 'registered_by').all()
    
    # Filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    priority_filter = request.GET.get('priority', '')
    
    if search_query:
        samples = samples.filter(
            Q(sample_id__icontains=search_query) |
            Q(source__icontains=search_query)
        )
    
    if status_filter:
        samples = samples.filter(status=status_filter)
    
    if type_filter:
        samples = samples.filter(sample_type=type_filter)
    
    if priority_filter:
        samples = samples.filter(priority=priority_filter)
    
    # Pagination
    paginator = Paginator(samples, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'sample_types': Sample.SAMPLE_TYPE_CHOICES,
        'statuses': Sample.STATUS_CHOICES,
        'priorities': Sample.PRIORITY_CHOICES,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'samples/sample_list.html', context)


@login_required
def sample_create(request):
    """Create a new sample."""
    if request.method == 'POST':
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.registered_by = request.user
            sample.save()
            messages.success(request, f'Sample {sample.sample_id} registered successfully.')
            return redirect('samples:sample_detail', pk=sample.pk)
    else:
        form = SampleForm()
    
    return render(request, 'samples/sample_form.html', {'form': form, 'action': 'Register'})


@login_required
def sample_detail(request, pk):
    """View sample details."""
    sample = get_object_or_404(
        Sample.objects.select_related('assigned_technician', 'registered_by')
        .prefetch_related('attachments', 'test_assignments'),
        pk=pk
    )
    
    # Handle attachment upload
    if request.method == 'POST':
        attachment_form = SampleAttachmentForm(request.POST, request.FILES)
        if attachment_form.is_valid():
            attachment = attachment_form.save(commit=False)
            attachment.sample = sample
            attachment.uploaded_by = request.user
            attachment.filename = request.FILES['file'].name
            attachment.save()
            messages.success(request, 'Attachment uploaded successfully.')
            return redirect('samples:sample_detail', pk=pk)
    else:
        attachment_form = SampleAttachmentForm()
    
    context = {
        'sample': sample,
        'attachment_form': attachment_form,
    }
    
    return render(request, 'samples/sample_detail.html', context)


@login_required
def sample_edit(request, pk):
    """Edit existing sample."""
    sample = get_object_or_404(Sample, pk=pk)
    
    if request.method == 'POST':
        form = SampleForm(request.POST, instance=sample)
        if form.is_valid():
            form.save()
            messages.success(request, f'Sample {sample.sample_id} updated successfully.')
            return redirect('samples:sample_detail', pk=pk)
    else:
        form = SampleForm(instance=sample)
    
    return render(request, 'samples/sample_form.html', {
        'form': form, 
        'action': 'Edit',
        'sample': sample
    })


@login_required
def sample_delete(request, pk):
    """Delete sample."""
    sample = get_object_or_404(Sample, pk=pk)
    
    if request.method == 'POST':
        sample_id = sample.sample_id
        sample.delete()
        messages.success(request, f'Sample {sample_id} deleted successfully.')
        return redirect('samples:sample_list')
    
    return render(request, 'samples/sample_confirm_delete.html', {'sample': sample})
