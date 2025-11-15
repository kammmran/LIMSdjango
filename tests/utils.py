"""Utility functions for test cost management."""
from decimal import Decimal
from django.db.models import Sum, Avg
from django.utils import timezone


def calculate_test_assignment_cost(test_assignment):
    """
    Calculate the total cost for a test assignment based on reagent usage.
    
    Args:
        test_assignment: TestAssignment instance
    
    Returns:
        Total cost as Decimal
    """
    from tests.models import ReagentUsage
    
    total_cost = test_assignment.reagent_usages.aggregate(
        total=Sum('total_cost')
    )['total'] or Decimal('0.00')
    
    # Update the actual_cost field
    test_assignment.actual_cost = total_cost
    test_assignment.save()
    
    return total_cost


def record_reagent_usage(test_assignment, reagent, quantity_used, user=None, notes=''):
    """
    Record reagent usage for a test assignment.
    
    Args:
        test_assignment: TestAssignment instance
        reagent: Reagent instance
        quantity_used: Quantity of reagent used
        user: User who used the reagent
        notes: Optional notes
    
    Returns:
        ReagentUsage instance
    """
    from tests.models import ReagentUsage
    from inventory.models import InventoryTransaction
    
    # Create reagent usage record
    usage = ReagentUsage.objects.create(
        test_assignment=test_assignment,
        reagent=reagent,
        quantity_used=quantity_used,
        used_by=user,
        notes=notes
    )
    
    # Create inventory transaction for stock reduction
    transaction = InventoryTransaction.objects.create(
        transaction_type='out',
        reagent=reagent,
        quantity=quantity_used,
        unit_cost=reagent.unit_cost,
        reason=f'Used for test {test_assignment.test.code} on sample {test_assignment.sample.sample_id}',
        performed_by=user
    )
    
    # Update reagent quantity
    reagent.quantity -= Decimal(str(quantity_used))
    reagent.save()
    
    # Recalculate test assignment cost
    calculate_test_assignment_cost(test_assignment)
    
    return usage


def get_test_cost_report(test, start_date=None, end_date=None):
    """
    Generate cost report for a specific test type.
    
    Args:
        test: Test instance
        start_date: Optional start date
        end_date: Optional end date
    
    Returns:
        Dictionary with cost statistics
    """
    from tests.models import TestAssignment
    
    assignments = TestAssignment.objects.filter(test=test)
    
    if start_date:
        assignments = assignments.filter(assigned_date__gte=start_date)
    if end_date:
        assignments = assignments.filter(assigned_date__lte=end_date)
    
    # Only completed tests
    completed_assignments = assignments.filter(status='completed')
    
    total_tests = completed_assignments.count()
    
    # Calculate costs
    total_actual_cost = completed_assignments.aggregate(
        total=Sum('actual_cost')
    )['total'] or Decimal('0.00')
    
    avg_cost_per_test = completed_assignments.aggregate(
        avg=Avg('actual_cost')
    )['avg'] or Decimal('0.00')
    
    # Calculate estimated vs actual
    total_estimated = test.estimated_cost * total_tests if test.estimated_cost else Decimal('0.00')
    variance = total_actual_cost - total_estimated
    
    # Revenue (if billable)
    total_revenue = test.billable_amount * total_tests if test.billable_amount else Decimal('0.00')
    profit = total_revenue - total_actual_cost
    
    return {
        'test_name': test.name,
        'test_code': test.code,
        'period_start': start_date,
        'period_end': end_date,
        'total_tests_completed': total_tests,
        'total_actual_cost': total_actual_cost,
        'average_cost_per_test': avg_cost_per_test,
        'estimated_cost_per_test': test.estimated_cost,
        'total_estimated_cost': total_estimated,
        'cost_variance': variance,
        'billable_amount_per_test': test.billable_amount,
        'total_revenue': total_revenue,
        'total_profit': profit,
    }


def get_sample_total_cost(sample):
    """
    Calculate total cost for all tests on a sample.
    
    Args:
        sample: Sample instance
    
    Returns:
        Total cost as Decimal
    """
    total = sample.test_assignments.aggregate(
        total=Sum('actual_cost')
    )['total'] or Decimal('0.00')
    
    return total


def get_reagent_test_usage_report(reagent, start_date=None, end_date=None):
    """
    Generate report of reagent usage across different tests.
    
    Args:
        reagent: Reagent instance
        start_date: Optional start date
        end_date: Optional end date
    
    Returns:
        Dictionary with usage statistics by test type
    """
    from tests.models import ReagentUsage
    
    usages = ReagentUsage.objects.filter(reagent=reagent)
    
    if start_date:
        usages = usages.filter(used_date__gte=start_date)
    if end_date:
        usages = usages.filter(used_date__lte=end_date)
    
    # Group by test
    test_usage = {}
    for usage in usages:
        test_code = usage.test_assignment.test.code
        test_name = usage.test_assignment.test.name
        
        if test_code not in test_usage:
            test_usage[test_code] = {
                'test_name': test_name,
                'quantity_used': Decimal('0.00'),
                'total_cost': Decimal('0.00'),
                'usage_count': 0,
            }
        
        test_usage[test_code]['quantity_used'] += usage.quantity_used
        test_usage[test_code]['total_cost'] += usage.total_cost or Decimal('0.00')
        test_usage[test_code]['usage_count'] += 1
    
    total_quantity = sum(data['quantity_used'] for data in test_usage.values())
    total_cost = sum(data['total_cost'] for data in test_usage.values())
    
    return {
        'reagent_name': reagent.name,
        'period_start': start_date,
        'period_end': end_date,
        'total_quantity_used': total_quantity,
        'total_cost': total_cost,
        'usage_by_test': test_usage,
    }


def get_cost_per_sample_report(start_date=None, end_date=None):
    """
    Generate report of costs per sample.
    
    Args:
        start_date: Optional start date
        end_date: Optional end date
    
    Returns:
        List of dictionaries with sample cost information
    """
    from samples.models import Sample
    from tests.models import TestAssignment
    
    samples = Sample.objects.all()
    
    if start_date:
        samples = samples.filter(received_date__gte=start_date)
    if end_date:
        samples = samples.filter(received_date__lte=end_date)
    
    sample_costs = []
    
    for sample in samples:
        total_cost = get_sample_total_cost(sample)
        test_count = sample.test_assignments.count()
        
        sample_costs.append({
            'sample_id': sample.sample_id,
            'sample_type': sample.get_sample_type_display(),
            'received_date': sample.received_date,
            'status': sample.get_status_display(),
            'test_count': test_count,
            'total_cost': total_cost,
            'avg_cost_per_test': total_cost / test_count if test_count > 0 else Decimal('0.00'),
        })
    
    # Sort by total cost descending
    sample_costs.sort(key=lambda x: x['total_cost'], reverse=True)
    
    total_samples = len(sample_costs)
    total_cost = sum(s['total_cost'] for s in sample_costs)
    avg_cost_per_sample = total_cost / total_samples if total_samples > 0 else Decimal('0.00')
    
    return {
        'period_start': start_date,
        'period_end': end_date,
        'total_samples': total_samples,
        'total_cost': total_cost,
        'average_cost_per_sample': avg_cost_per_sample,
        'samples': sample_costs,
    }


def update_test_estimated_costs():
    """
    Update estimated costs for all tests based on historical actual costs.
    
    Returns:
        Number of tests updated
    """
    from tests.models import Test, TestAssignment
    
    updated = 0
    
    for test in Test.objects.filter(is_active=True):
        # Get average actual cost from completed test assignments
        avg_cost = TestAssignment.objects.filter(
            test=test,
            status='completed',
            actual_cost__isnull=False
        ).aggregate(avg=Avg('actual_cost'))['avg']
        
        if avg_cost and avg_cost > 0:
            test.estimated_cost = avg_cost
            test.save()
            updated += 1
    
    return updated
