"""Utility functions for sample and test time management."""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q


def get_overdue_samples():
    """Get all samples that have passed their deadline."""
    from samples.models import Sample
    
    now = timezone.now()
    overdue = Sample.objects.filter(
        completion_deadline__lt=now
    ).exclude(
        status__in=['completed', 'archived']
    )
    
    return overdue


def get_samples_deadline_approaching(hours=24):
    """
    Get samples with deadlines approaching within specified hours.
    
    Args:
        hours: Number of hours to look ahead
    
    Returns:
        QuerySet of samples
    """
    from samples.models import Sample
    
    now = timezone.now()
    threshold = now + timedelta(hours=hours)
    
    approaching = Sample.objects.filter(
        completion_deadline__gte=now,
        completion_deadline__lte=threshold
    ).exclude(
        status__in=['completed', 'archived']
    )
    
    return approaching


def get_overdue_tests():
    """Get all test assignments that have passed their deadline."""
    from tests.models import TestAssignment
    
    now = timezone.now()
    overdue = TestAssignment.objects.filter(
        deadline__lt=now
    ).exclude(
        status='completed'
    )
    
    return overdue


def get_tests_deadline_approaching(hours=12):
    """
    Get test assignments with deadlines approaching within specified hours.
    
    Args:
        hours: Number of hours to look ahead
    
    Returns:
        QuerySet of test assignments
    """
    from tests.models import TestAssignment
    
    now = timezone.now()
    threshold = now + timedelta(hours=hours)
    
    approaching = TestAssignment.objects.filter(
        deadline__gte=now,
        deadline__lte=threshold
    ).exclude(
        status='completed'
    )
    
    return approaching


def set_sample_deadline(sample, deadline_hours=None, deadline_datetime=None):
    """
    Set deadline for a sample.
    
    Args:
        sample: Sample instance
        deadline_hours: Hours from now for deadline (alternative to deadline_datetime)
        deadline_datetime: Specific datetime for deadline
    """
    if deadline_datetime:
        sample.completion_deadline = deadline_datetime
    elif deadline_hours:
        sample.completion_deadline = timezone.now() + timedelta(hours=deadline_hours)
    else:
        # Default based on priority
        priority_hours = {
            'urgent': 4,
            'high': 24,
            'normal': 72,
            'low': 168,
        }
        hours = priority_hours.get(sample.priority, 72)
        sample.completion_deadline = timezone.now() + timedelta(hours=hours)
    
    sample.save()
    return sample


def set_test_deadline(test_assignment):
    """
    Set deadline for a test assignment based on turnaround time.
    
    Args:
        test_assignment: TestAssignment instance
    """
    if test_assignment.test.turnaround_time:
        test_assignment.deadline = timezone.now() + timedelta(
            hours=test_assignment.test.turnaround_time
        )
        test_assignment.save()
    
    return test_assignment


def calculate_expected_completion(sample):
    """
    Calculate expected completion date based on assigned tests.
    
    Args:
        sample: Sample instance
    
    Returns:
        datetime of expected completion
    """
    from tests.models import TestAssignment
    
    test_assignments = sample.test_assignments.all()
    
    if not test_assignments:
        return None
    
    # Find the latest expected completion among all assigned tests
    latest_completion = None
    
    for assignment in test_assignments:
        if assignment.expected_completion:
            if not latest_completion or assignment.expected_completion > latest_completion:
                latest_completion = assignment.expected_completion
    
    return latest_completion


def get_sample_workload_report(start_date=None, end_date=None):
    """
    Generate workload report showing samples and tests by status and deadline.
    
    Args:
        start_date: Optional start date
        end_date: Optional end date
    
    Returns:
        Dictionary with workload statistics
    """
    from samples.models import Sample
    from tests.models import TestAssignment
    
    if not start_date:
        start_date = timezone.now()
    if not end_date:
        end_date = timezone.now() + timedelta(days=7)
    
    # Samples in the period
    samples_in_period = Sample.objects.filter(
        completion_deadline__gte=start_date,
        completion_deadline__lte=end_date
    ).exclude(status__in=['completed', 'archived'])
    
    # Tests in the period
    tests_in_period = TestAssignment.objects.filter(
        deadline__gte=start_date,
        deadline__lte=end_date
    ).exclude(status='completed')
    
    # Group by status
    sample_status_counts = {}
    for status, _ in Sample.STATUS_CHOICES:
        count = samples_in_period.filter(status=status).count()
        sample_status_counts[status] = count
    
    test_status_counts = {}
    for status, _ in TestAssignment.STATUS_CHOICES:
        count = tests_in_period.filter(status=status).count()
        test_status_counts[status] = count
    
    return {
        'period_start': start_date,
        'period_end': end_date,
        'total_samples': samples_in_period.count(),
        'total_tests': tests_in_period.count(),
        'samples_by_status': sample_status_counts,
        'tests_by_status': test_status_counts,
        'overdue_samples': get_overdue_samples().count(),
        'overdue_tests': get_overdue_tests().count(),
    }


def get_technician_workload(technician, include_completed=False):
    """
    Get workload summary for a specific technician.
    
    Args:
        technician: User instance
        include_completed: Whether to include completed items
    
    Returns:
        Dictionary with workload information
    """
    from samples.models import Sample
    from tests.models import TestAssignment
    
    # Assigned samples
    samples = Sample.objects.filter(assigned_technician=technician)
    if not include_completed:
        samples = samples.exclude(status__in=['completed', 'archived'])
    
    # Assigned tests
    tests = TestAssignment.objects.filter(assigned_to=technician)
    if not include_completed:
        tests = tests.exclude(status='completed')
    
    # Overdue items
    now = timezone.now()
    overdue_samples = samples.filter(completion_deadline__lt=now)
    overdue_tests = tests.filter(deadline__lt=now)
    
    # Due today
    end_of_day = now.replace(hour=23, minute=59, second=59)
    due_today_samples = samples.filter(
        completion_deadline__gte=now,
        completion_deadline__lte=end_of_day
    )
    due_today_tests = tests.filter(
        deadline__gte=now,
        deadline__lte=end_of_day
    )
    
    return {
        'technician': technician.get_full_name() or technician.username,
        'total_samples': samples.count(),
        'total_tests': tests.count(),
        'overdue_samples': overdue_samples.count(),
        'overdue_tests': overdue_tests.count(),
        'due_today_samples': due_today_samples.count(),
        'due_today_tests': due_today_tests.count(),
        'samples': samples,
        'tests': tests,
    }
