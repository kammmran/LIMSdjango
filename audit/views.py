from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import AuditLog


@login_required
def audit_log_list(request):
    """List audit logs with filtering."""
    logs = AuditLog.objects.select_related('user').all()
    
    # Filters
    user_filter = request.GET.get('user')
    action_filter = request.GET.get('action')
    model_filter = request.GET.get('model')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if user_filter:
        logs = logs.filter(user_id=user_filter)
    if action_filter:
        logs = logs.filter(action=action_filter)
    if model_filter:
        logs = logs.filter(model_name=model_filter)
    if start_date:
        logs = logs.filter(timestamp__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__lte=end_date)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique users and models for filters
    from users.models import User
    users = User.objects.filter(is_active=True)
    models = AuditLog.objects.values_list('model_name', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'actions': AuditLog.ACTION_CHOICES,
        'models': models,
        'user_filter': user_filter,
        'action_filter': action_filter,
        'model_filter': model_filter,
    }
    
    return render(request, 'audit/audit_log_list.html', context)
