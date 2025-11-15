from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F
from datetime import datetime, timedelta
from samples.models import Sample
from tests.models import Test, TestAssignment
from inventory.models import Reagent, StockItem
from instruments.models import Instrument
from audit.models import AuditLog


@login_required
def dashboard_view(request):
    """Main dashboard view with key metrics and charts."""
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    # Import TestResult for pending reviews
    from results.models import TestResult
    
    # Key Metrics
    total_samples_today = Sample.objects.filter(received_date=today).count()
    pending_tests = TestAssignment.objects.filter(status='assigned').count()
    completed_tests = TestAssignment.objects.filter(status='completed').count()
    pending_reviews = TestResult.objects.filter(status='pending_review').count()
    instruments_needing_calibration = Instrument.objects.filter(
        next_calibration_date__lte=today + timedelta(days=30)
    ).count()
    low_stock_alerts = StockItem.objects.filter(
        quantity__lte=F('minimum_quantity')
    ).count() + Reagent.objects.filter(
        quantity__lte=F('minimum_quantity')
    ).count()
    
    # Activity Feed - Recent samples and activities
    recent_samples = Sample.objects.order_by('-received_date')[:10]
    recent_activities = AuditLog.objects.order_by('-timestamp')[:15]
    
    # Pending reviews list
    pending_review_list = TestResult.objects.filter(
        status='pending_review'
    ).select_related('test_assignment__sample', 'test_assignment__test', 'entered_by').order_by('-entered_date')[:10]
    
    # Weekly sample count for chart
    weekly_samples = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        count = Sample.objects.filter(received_date=date).count()
        weekly_samples.append({
            'date': date.strftime('%m/%d'),
            'count': count
        })
    
    # Test categories for pie chart
    test_categories = Test.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_samples_today': total_samples_today,
        'pending_tests': pending_tests,
        'completed_tests': completed_tests,
        'pending_reviews': pending_reviews,
        'pending_review_list': pending_review_list,
        'instruments_needing_calibration': instruments_needing_calibration,
        'low_stock_alerts': low_stock_alerts,
        'recent_samples': recent_samples,
        'recent_activities': recent_activities,
        'weekly_samples': weekly_samples,
        'test_categories': test_categories,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
