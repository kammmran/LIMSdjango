from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from tests.models import TestAssignment
from .models import TestResult, ParameterResult


@login_required
def result_list(request):
    """List all results."""
    results = TestResult.objects.select_related(
        'test_assignment__sample',
        'test_assignment__test',
        'entered_by'
    ).order_by('-entered_date')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        results = results.filter(status=status_filter)
    
    context = {
        'results': results,
        'statuses': TestResult.STATUS_CHOICES,
        'status_filter': status_filter,
    }
    
    return render(request, 'results/result_list.html', context)


@login_required
def enter_result(request, assignment_id):
    """Enter results for a test assignment."""
    assignment = get_object_or_404(
        TestAssignment.objects.select_related('sample', 'test').prefetch_related('test__parameters'),
        pk=assignment_id
    )
    
    # Get or create result
    result, created = TestResult.objects.get_or_create(
        test_assignment=assignment,
        defaults={'entered_by': request.user}
    )
    
    if request.method == 'POST':
        result.comments = request.POST.get('comments', '')
        
        # Handle file upload
        if 'instrument_file' in request.FILES:
            result.instrument_file = request.FILES['instrument_file']
        
        # Handle parameter results
        for parameter in assignment.test.parameters.all():
            value_numeric = request.POST.get(f'param_numeric_{parameter.id}')
            value_text = request.POST.get(f'param_text_{parameter.id}')
            param_notes = request.POST.get(f'param_notes_{parameter.id}', '')
            
            param_result, _ = ParameterResult.objects.get_or_create(
                test_result=result,
                parameter=parameter
            )
            
            if value_numeric:
                param_result.value_numeric = value_numeric
                param_result.check_abnormal()
            if value_text:
                param_result.value_text = value_text
            
            param_result.notes = param_notes
            param_result.save()
        
        # Update status
        action = request.POST.get('action')
        if action == 'save_draft':
            result.status = 'draft'
        elif action == 'submit_review':
            result.status = 'pending_review'
            assignment.status = 'waiting_review'
            assignment.save()
        
        result.save()
        messages.success(request, 'Results saved successfully.')
        
        if action == 'submit_review':
            return redirect('results:review_results')
        return redirect('results:result_list')
    
    context = {
        'assignment': assignment,
        'result': result,
        'parameter_results': {
            pr.parameter_id: pr for pr in result.parameter_results.all()
        }
    }
    
    return render(request, 'results/enter_result.html', context)


@login_required
def review_results(request):
    """List results pending review."""
    results = TestResult.objects.filter(
        status='pending_review'
    ).select_related(
        'test_assignment__sample',
        'test_assignment__test',
        'entered_by'
    ).prefetch_related('parameter_results')
    
    return render(request, 'results/review_results.html', {'results': results})


@login_required
def approve_result(request, pk):
    """Approve a result."""
    if request.method == 'POST':
        result = get_object_or_404(TestResult, pk=pk)
        result.status = 'approved'
        result.reviewed_by = request.user
        result.reviewed_date = timezone.now()
        result.reviewer_comments = request.POST.get('reviewer_comments', '')
        result.save()
        
        # Update test assignment
        result.test_assignment.status = 'completed'
        result.test_assignment.completed_date = timezone.now()
        result.test_assignment.save()
        
        messages.success(request, 'Result approved successfully.')
        return redirect('results:review_results')
    
    return redirect('results:result_list')


@login_required
def reject_result(request, pk):
    """Reject a result."""
    if request.method == 'POST':
        result = get_object_or_404(TestResult, pk=pk)
        result.status = 'rejected'
        result.reviewed_by = request.user
        result.reviewed_date = timezone.now()
        result.reviewer_comments = request.POST.get('reviewer_comments', '')
        result.save()
        
        # Update test assignment
        result.test_assignment.status = 'assigned'
        result.test_assignment.save()
        
        messages.warning(request, 'Result rejected. Please re-enter the results.')
        return redirect('results:review_results')
    
    return redirect('results:result_list')


@login_required
def approved_results(request):
    """List approved results."""
    results = TestResult.objects.filter(
        status='approved'
    ).select_related(
        'test_assignment__sample',
        'test_assignment__test',
        'entered_by',
        'reviewed_by'
    ).order_by('-reviewed_date')
    
    return render(request, 'results/approved_results.html', {'results': results})


@login_required
def export_result(request, pk):
    """Export result as CSV."""
    result = get_object_or_404(
        TestResult.objects.select_related(
            'test_assignment__sample',
            'test_assignment__test'
        ).prefetch_related('parameter_results__parameter'),
        pk=pk
    )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="result_{result.test_assignment.sample.sample_id}_{result.test_assignment.test.code}.csv"'
    
    import csv
    writer = csv.writer(response)
    writer.writerow(['Sample ID', result.test_assignment.sample.sample_id])
    writer.writerow(['Test', result.test_assignment.test.name])
    writer.writerow(['Status', result.get_status_display()])
    writer.writerow(['Entered By', result.entered_by.get_full_name()])
    writer.writerow(['Entered Date', result.entered_date])
    writer.writerow([])
    writer.writerow(['Parameter', 'Value', 'Unit', 'Reference Range', 'Status'])
    
    for pr in result.parameter_results.all():
        value = pr.value_numeric if pr.value_numeric else pr.value_text
        ref_range = ''
        if pr.parameter.reference_range_min and pr.parameter.reference_range_max:
            ref_range = f"{pr.parameter.reference_range_min} - {pr.parameter.reference_range_max}"
        elif pr.parameter.reference_range_text:
            ref_range = pr.parameter.reference_range_text
        
        status = 'Abnormal' if pr.is_abnormal else 'Normal'
        writer.writerow([pr.parameter.name, value, pr.parameter.unit, ref_range, status])
    
    return response
