from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
import json
from datetime import datetime, timedelta
from .models import Instrument, CalibrationRecord, MaintenanceLog, InstrumentBorrowing


@login_required
def instrument_list(request):
    """List all instruments."""
    instruments = Instrument.objects.all()
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        instruments = instruments.filter(status=status_filter)
    
    context = {
        'instruments': instruments,
        'statuses': Instrument.STATUS_CHOICES,
        'status_filter': status_filter,
    }
    
    return render(request, 'instruments/instrument_list.html', context)


@login_required
def instrument_create(request):
    """Create new instrument."""
    if request.method == 'POST':
        instrument = Instrument.objects.create(
            name=request.POST['name'],
            model=request.POST['model'],
            serial_number=request.POST['serial_number'],
            manufacturer=request.POST['manufacturer'],
            location=request.POST['location'],
            status=request.POST.get('status', 'operational'),
            purchase_date=request.POST.get('purchase_date') or None,
            calibration_frequency=request.POST.get('calibration_frequency', 365),
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Instrument added successfully.')
        return redirect('instruments:instrument_list')
    
    return render(request, 'instruments/instrument_form.html', {'action': 'Create'})


@login_required
def instrument_edit(request, pk):
    """Edit instrument."""
    instrument = get_object_or_404(Instrument, pk=pk)
    
    if request.method == 'POST':
        instrument.name = request.POST['name']
        instrument.model = request.POST['model']
        instrument.serial_number = request.POST['serial_number']
        instrument.manufacturer = request.POST['manufacturer']
        instrument.location = request.POST['location']
        instrument.status = request.POST.get('status', 'operational')
        instrument.purchase_date = request.POST.get('purchase_date') or None
        instrument.calibration_frequency = request.POST.get('calibration_frequency', 365)
        instrument.notes = request.POST.get('notes', '')
        instrument.save()
        messages.success(request, 'Instrument updated successfully.')
        return redirect('instruments:instrument_list')
    
    return render(request, 'instruments/instrument_form.html', {'instrument': instrument, 'action': 'Edit'})


@login_required
def instrument_detail(request, pk):
    """View instrument details."""
    instrument = get_object_or_404(
        Instrument.objects.prefetch_related('calibrations', 'maintenance_logs'),
        pk=pk
    )
    
    recent_calibrations = instrument.calibrations.all()[:5]
    recent_maintenance = instrument.maintenance_logs.all()[:5]
    
    context = {
        'instrument': instrument,
        'recent_calibrations': recent_calibrations,
        'recent_maintenance': recent_maintenance,
    }
    
    return render(request, 'instruments/instrument_detail.html', context)


@login_required
def calibration_list(request):
    """List all calibration records."""
    calibrations = CalibrationRecord.objects.select_related(
        'instrument', 'performed_by'
    ).order_by('-calibration_date')
    
    return render(request, 'instruments/calibration_list.html', {'calibrations': calibrations})


@login_required
def calibration_add(request, instrument_id):
    """Add calibration record."""
    instrument = get_object_or_404(Instrument, pk=instrument_id)
    
    if request.method == 'POST':
        from datetime import datetime, timedelta
        
        calibration_date = request.POST['calibration_date']
        next_calibration_date = request.POST['next_calibration_date']
        
        calibration = CalibrationRecord.objects.create(
            instrument=instrument,
            calibration_date=calibration_date,
            next_calibration_date=next_calibration_date,
            performed_by=request.user,
            standards_used=request.POST['standards_used'],
            results=request.POST['results'],
            passed=request.POST.get('passed') == 'on',
            notes=request.POST.get('notes', '')
        )
        
        if 'certificate_file' in request.FILES:
            calibration.certificate_file = request.FILES['certificate_file']
            calibration.save()
        
        # Update instrument
        instrument.last_calibration_date = calibration_date
        instrument.next_calibration_date = next_calibration_date
        instrument.save()
        
        messages.success(request, 'Calibration record added successfully.')
        return redirect('instruments:instrument_detail', pk=instrument_id)
    
    return render(request, 'instruments/calibration_form.html', {'instrument': instrument})


@login_required
def maintenance_list(request):
    """List all maintenance logs."""
    logs = MaintenanceLog.objects.select_related(
        'instrument', 'performed_by'
    ).order_by('-maintenance_date')
    
    return render(request, 'instruments/maintenance_list.html', {'logs': logs})


@login_required
def maintenance_add(request, instrument_id):
    """Add maintenance log."""
    instrument = get_object_or_404(Instrument, pk=instrument_id)
    
    if request.method == 'POST':
        log = MaintenanceLog.objects.create(
            instrument=instrument,
            maintenance_type=request.POST['maintenance_type'],
            maintenance_date=request.POST['maintenance_date'],
            performed_by=request.user,
            description=request.POST['description'],
            parts_replaced=request.POST.get('parts_replaced', ''),
            cost=request.POST.get('cost') or None,
            downtime_hours=request.POST.get('downtime_hours') or None,
            notes=request.POST.get('notes', '')
        )
        
        messages.success(request, 'Maintenance log added successfully.')
        return redirect('instruments:instrument_detail', pk=instrument_id)
    
    return render(request, 'instruments/maintenance_form.html', {'instrument': instrument})


# ============================================================
# Instrument Borrowing Views
# ============================================================

@login_required
def borrowing_list(request):
    """List all instrument borrowings with filters"""
    borrowings = InstrumentBorrowing.objects.select_related(
        'instrument', 'borrower_user', 'borrower_lab', 'borrower_person', 
        'sample', 'approved_by', 'created_by'
    ).all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        borrowings = borrowings.filter(status=status_filter)
    
    # Filter by borrower type
    borrower_type = request.GET.get('borrower_type')
    if borrower_type:
        borrowings = borrowings.filter(borrower_type=borrower_type)
    
    # Filter by instrument
    instrument_id = request.GET.get('instrument')
    if instrument_id:
        borrowings = borrowings.filter(instrument_id=instrument_id)
    
    # Search
    search = request.GET.get('search')
    if search:
        borrowings = borrowings.filter(
            Q(borrower_name__icontains=search) |
            Q(instrument__name__icontains=search) |
            Q(purpose_description__icontains=search)
        )
    
    # Get statistics
    stats = {
        'total': borrowings.count(),
        'pending': borrowings.filter(status='pending').count(),
        'borrowed': borrowings.filter(status='borrowed').count(),
        'overdue': borrowings.filter(status='overdue').count(),
        'returned': borrowings.filter(status='returned').count(),
    }
    
    # Get available instruments
    instruments = Instrument.objects.filter(status='operational')
    
    context = {
        'borrowings': borrowings.order_by('-requested_date'),
        'stats': stats,
        'status_filter': status_filter,
        'borrower_type': borrower_type,
        'search': search,
        'instruments': instruments,
        'status_choices': InstrumentBorrowing.STATUS_CHOICES,
        'borrower_type_choices': InstrumentBorrowing.BORROWER_TYPE_CHOICES,
    }
    
    return render(request, 'instruments/borrowing_list.html', context)


@login_required
def borrowing_detail(request, pk):
    """View borrowing details"""
    borrowing = get_object_or_404(
        InstrumentBorrowing.objects.select_related(
            'instrument', 'borrower_user', 'borrower_lab', 
            'borrower_person', 'sample', 'approved_by', 'created_by'
        ),
        pk=pk
    )
    
    context = {
        'borrowing': borrowing,
    }
    
    return render(request, 'instruments/borrowing_detail.html', context)


@login_required
def borrowing_create(request):
    """Create a new borrowing request"""
    if request.method == 'POST':
        try:
            borrowing = InstrumentBorrowing.objects.create(
                instrument_id=request.POST['instrument'],
                borrower_type=request.POST['borrower_type'],
                borrower_name=request.POST['borrower_name'],
                borrower_email=request.POST.get('borrower_email', ''),
                borrower_phone=request.POST.get('borrower_phone', ''),
                purpose=request.POST['purpose'],
                purpose_description=request.POST['purpose_description'],
                location_of_use=request.POST['location_of_use'],
                requested_start_date=request.POST['requested_start_date'],
                requested_end_date=request.POST['requested_end_date'],
                accessories_borrowed=request.POST.get('accessories_borrowed', ''),
                special_instructions=request.POST.get('special_instructions', ''),
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )
            
            # Link to user if internal
            if request.POST.get('borrower_user'):
                borrowing.borrower_user_id = request.POST['borrower_user']
            
            # Link to lab if selected
            if request.POST.get('borrower_lab'):
                borrowing.borrower_lab_id = request.POST['borrower_lab']
            
            # Link to person if selected
            if request.POST.get('borrower_person'):
                borrowing.borrower_person_id = request.POST['borrower_person']
            
            # Link to sample if selected
            if request.POST.get('sample'):
                borrowing.sample_id = request.POST['sample']
            
            borrowing.save()
            
            messages.success(request, f'Borrowing request for {borrowing.instrument.name} created successfully!')
            return redirect('instruments:borrowing_detail', pk=borrowing.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating borrowing request: {str(e)}')
    
    # Get available instruments
    instruments = Instrument.objects.filter(status='operational').order_by('name')
    
    # Get labs and people for dropdown
    try:
        from labs.models import Lab, Person
        labs = Lab.objects.filter(is_active=True).order_by('name')
        people = Person.objects.filter(is_active=True).order_by('last_name', 'first_name')
    except:
        labs = []
        people = []
    
    # Get samples
    try:
        from samples.models import Sample
        samples = Sample.objects.filter(status__in=['registered', 'in_progress']).order_by('-sample_id')[:100]
    except:
        samples = []
    
    context = {
        'instruments': instruments,
        'labs': labs,
        'people': people,
        'samples': samples,
        'borrower_type_choices': InstrumentBorrowing.BORROWER_TYPE_CHOICES,
        'purpose_choices': InstrumentBorrowing.PURPOSE_CHOICES,
    }
    
    return render(request, 'instruments/borrowing_form.html', context)


@login_required
def borrowing_approve(request, pk):
    """Approve a borrowing request"""
    borrowing = get_object_or_404(InstrumentBorrowing, pk=pk)
    
    if request.method == 'POST':
        borrowing.status = 'approved'
        borrowing.approved_by = request.user
        borrowing.approval_date = timezone.now()
        borrowing.save()
        
        messages.success(request, f'Borrowing request approved for {borrowing.borrower_name}')
        return redirect('instruments:borrowing_detail', pk=pk)
    
    return redirect('instruments:borrowing_detail', pk=pk)


@login_required
def borrowing_checkout(request, pk):
    """Mark instrument as checked out/borrowed"""
    borrowing = get_object_or_404(InstrumentBorrowing, pk=pk)
    
    if request.method == 'POST':
        borrowing.status = 'borrowed'
        borrowing.actual_borrow_date = timezone.now()
        borrowing.condition_at_checkout = request.POST.get('condition_at_checkout', '')
        borrowing.save()
        
        messages.success(request, f'Instrument {borrowing.instrument.name} checked out to {borrowing.borrower_name}')
        return redirect('instruments:borrowing_detail', pk=pk)
    
    return render(request, 'instruments/borrowing_checkout.html', {'borrowing': borrowing})


@login_required
def borrowing_return(request, pk):
    """Mark instrument as returned"""
    borrowing = get_object_or_404(InstrumentBorrowing, pk=pk)
    
    if request.method == 'POST':
        borrowing.status = 'returned'
        borrowing.actual_return_date = timezone.now()
        borrowing.condition_at_return = request.POST.get('condition_at_return', '')
        borrowing.save()
        
        messages.success(request, f'Instrument {borrowing.instrument.name} returned by {borrowing.borrower_name}')
        return redirect('instruments:borrowing_detail', pk=pk)
    
    return render(request, 'instruments/borrowing_return.html', {'borrowing': borrowing})


@login_required
def borrowing_cancel(request, pk):
    """Cancel a borrowing request"""
    borrowing = get_object_or_404(InstrumentBorrowing, pk=pk)
    
    if request.method == 'POST':
        borrowing.status = 'cancelled'
        borrowing.save()
        
        messages.success(request, 'Borrowing request cancelled')
        return redirect('instruments:borrowing_list')
    
    return render(request, 'instruments/borrowing_confirm_cancel.html', {'borrowing': borrowing})


@login_required
def borrowing_timeline(request):
    """Time-based view of all borrowed items"""
    from datetime import datetime, timedelta
    
    # Get date range from request or default to current month
    today = timezone.now()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        # Default to current month
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Get last day of month
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
        end_date = end_date.replace(hour=23, minute=59, second=59)
    
    # Get all borrowings that overlap with this date range
    borrowings = InstrumentBorrowing.objects.select_related(
        'instrument', 'borrower_user', 'borrower_lab', 'borrower_person'
    ).filter(
        Q(requested_start_date__lte=end_date) & 
        Q(requested_end_date__gte=start_date)
    ).exclude(status='cancelled').order_by('requested_start_date')
    
    # Get currently borrowed items
    currently_borrowed = InstrumentBorrowing.objects.filter(
        status='borrowed'
    ).select_related('instrument', 'borrower_user').order_by('requested_end_date')
    
    # Get overdue items
    overdue_items = InstrumentBorrowing.objects.filter(
        status='overdue'
    ).select_related('instrument', 'borrower_user').order_by('requested_end_date')
    
    # Upcoming borrowings (next 7 days)
    upcoming = InstrumentBorrowing.objects.filter(
        status__in=['approved', 'pending'],
        requested_start_date__gte=today,
        requested_start_date__lte=today + timedelta(days=7)
    ).select_related('instrument', 'borrower_user').order_by('requested_start_date')
    
    # Prepare data for Gantt chart
    # Get all instruments that have borrowings
    instruments_with_borrowings = Instrument.objects.filter(
        id__in=borrowings.values_list('instrument_id', flat=True)
    ).distinct()
    
    # Serialize instruments data
    instruments_json = json.dumps([{
        'id': inst.id,
        'name': inst.name,
        'serial_number': inst.serial_number or 'N/A',
        'location': inst.location or 'Not specified',
    } for inst in instruments_with_borrowings])
    
    # Serialize borrowings data
    borrowings_json = json.dumps([{
        'id': b.id,
        'instrument_id': b.instrument.id,
        'borrower_name': b.borrower_display,
        'purpose': b.get_purpose_display(),
        'start_date': b.actual_borrow_date.isoformat() if b.actual_borrow_date else b.requested_start_date.isoformat(),
        'end_date': b.actual_return_date.isoformat() if b.actual_return_date else b.requested_end_date.isoformat(),
        'status': b.status,
        'status_display': b.get_status_display(),
        'duration': b.requested_duration_hours,
        'is_overdue': b.is_overdue,
        'days_overdue': b.days_overdue if b.is_overdue else 0,
    } for b in borrowings])
    
    context = {
        'borrowings': borrowings,
        'currently_borrowed': currently_borrowed,
        'overdue_items': overdue_items,
        'upcoming': upcoming,
        'start_date': start_date,
        'end_date': end_date,
        'today': today,
        'instruments_json': instruments_json,
        'borrowings_json': borrowings_json,
    }
    
    return render(request, 'instruments/borrowing_timeline.html', context)
    return render(request, 'instruments/borrowing_timeline.html', context)
