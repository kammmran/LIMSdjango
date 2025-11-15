from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Test, TestParameter, TestAssignment
from samples.models import Sample


@login_required
def test_list(request):
    """List all test assignments."""
    assignments = TestAssignment.objects.select_related(
        'sample', 'test', 'assigned_to'
    ).order_by('-assigned_date')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        assignments = assignments.filter(status=status_filter)
    
    context = {
        'assignments': assignments,
        'statuses': TestAssignment.STATUS_CHOICES,
        'status_filter': status_filter,
    }
    
    return render(request, 'tests/test_list.html', context)


@login_required
def test_type_list(request):
    """List all test types."""
    tests = Test.objects.prefetch_related('parameters').filter(is_active=True)
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        tests = tests.filter(category=category_filter)
    
    context = {
        'tests': tests,
        'categories': Test.CATEGORY_CHOICES,
        'category_filter': category_filter,
    }
    
    return render(request, 'tests/test_type_list.html', context)


@login_required
def test_type_create(request):
    """Create new test type."""
    if request.method == 'POST':
        # Handle test creation
        name = request.POST.get('name')
        code = request.POST.get('test_code')  # Fixed: form field is 'test_code'
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        turnaround_time = request.POST.get('turnaround_time')
        
        test = Test.objects.create(
            name=name,
            code=code,
            category=category,
            description=description,
            turnaround_time=turnaround_time if turnaround_time else 24
        )
        
        # Handle parameters
        param_names = request.POST.getlist('param_names[]')
        param_units = request.POST.getlist('param_units[]')
        param_ranges = request.POST.getlist('param_ranges[]')
        
        for i, name in enumerate(param_names):
            if name.strip():
                reference_range = param_ranges[i] if i < len(param_ranges) else ''
                TestParameter.objects.create(
                    test=test,
                    name=name,
                    unit=param_units[i] if i < len(param_units) else '',
                    reference_range_text=reference_range,
                    order=i
                )
        
        messages.success(request, f'Test type {test.code} created successfully.')
        return redirect('tests:test_type_list')
    
    return render(request, 'tests/test_type_form.html', {'action': 'Create'})


@login_required
def test_type_edit(request, pk):
    """Edit test type."""
    test = get_object_or_404(Test, pk=pk)
    
    if request.method == 'POST':
        test.name = request.POST.get('name')
        test.code = request.POST.get('test_code')  # Fixed: form field is 'test_code'
        test.category = request.POST.get('category')
        test.description = request.POST.get('description', '')
        turnaround_time = request.POST.get('turnaround_time')
        test.turnaround_time = turnaround_time if turnaround_time else 24
        test.save()
        
        # Update parameters (simple approach: delete and recreate)
        test.parameters.all().delete()
        
        param_names = request.POST.getlist('param_names[]')
        param_units = request.POST.getlist('param_units[]')
        param_ranges = request.POST.getlist('param_ranges[]')
        
        for i, name in enumerate(param_names):
            if name.strip():
                reference_range = param_ranges[i] if i < len(param_ranges) else ''
                TestParameter.objects.create(
                    test=test,
                    name=name,
                    unit=param_units[i] if i < len(param_units) else '',
                    reference_range_text=reference_range,
                    order=i
                )
        
        messages.success(request, f'Test type {test.code} updated successfully.')
        return redirect('tests:test_type_list')
    
    # Get current parameters for display
    parameters = test.parameters.all()
    
    context = {
        'test': test,
        'parameters': parameters,
        'action': 'Edit'
    }
    
    return render(request, 'tests/test_type_form.html', context)


@login_required
def assign_test(request):
    """Assign tests to samples."""
    if request.method == 'POST':
        sample_id = request.POST.get('sample')
        test_ids = request.POST.getlist('tests')
        assigned_to_id = request.POST.get('assigned_to')
        
        sample = get_object_or_404(Sample, pk=sample_id)
        
        for test_id in test_ids:
            test = get_object_or_404(Test, pk=test_id)
            
            # Check if already assigned
            if not TestAssignment.objects.filter(sample=sample, test=test).exists():
                TestAssignment.objects.create(
                    sample=sample,
                    test=test,
                    assigned_to_id=assigned_to_id if assigned_to_id else None,
                    assigned_by=request.user
                )
        
        messages.success(request, f'{len(test_ids)} test(s) assigned to sample {sample.sample_id}.')
        return redirect('samples:sample_detail', pk=sample.pk)
    
    samples = Sample.objects.filter(status__in=['registered', 'in_progress'])
    tests = Test.objects.filter(is_active=True)
    
    from users.models import User
    technicians = User.objects.filter(
        role__can_enter_results=True,
        is_active=True
    )
    
    context = {
        'samples': samples,
        'tests': tests,
        'technicians': technicians,
    }
    
    return render(request, 'tests/assign_test.html', context)


@login_required
def test_workflow(request):
    """Kanban-style test workflow view."""
    assigned = TestAssignment.objects.filter(status='assigned').select_related('sample', 'test', 'assigned_to')
    in_progress = TestAssignment.objects.filter(status='in_progress').select_related('sample', 'test', 'assigned_to')
    waiting_review = TestAssignment.objects.filter(status='waiting_review').select_related('sample', 'test', 'assigned_to')
    completed = TestAssignment.objects.filter(status='completed').select_related('sample', 'test', 'assigned_to')[:20]
    
    context = {
        'assigned': assigned,
        'in_progress': in_progress,
        'waiting_review': waiting_review,
        'completed': completed,
    }
    
    return render(request, 'tests/test_workflow.html', context)


@login_required
def update_assignment_status(request, pk):
    """Update test assignment status."""
    if request.method == 'POST':
        assignment = get_object_or_404(TestAssignment, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(TestAssignment.STATUS_CHOICES):
            assignment.status = new_status
            
            if new_status == 'in_progress' and not assignment.started_date:
                assignment.started_date = timezone.now()
            elif new_status == 'completed' and not assignment.completed_date:
                assignment.completed_date = timezone.now()
            
            assignment.save()
            messages.success(request, 'Test status updated successfully.')
        
        return redirect('tests:test_workflow')
    
    return redirect('tests:test_list')
