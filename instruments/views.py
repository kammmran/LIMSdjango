from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Instrument, CalibrationRecord, MaintenanceLog


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
