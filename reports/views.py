from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import datetime, timedelta
from samples.models import Sample
from tests.models import TestAssignment
from inventory.models import Reagent, StockItem
from instruments.models import Instrument
import csv


@login_required
def report_dashboard(request):
    """Reports dashboard."""
    return render(request, 'reports/dashboard.html')


@login_required
def sample_report(request):
    """Generate sample report."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    sample_type = request.GET.get('sample_type')
    status = request.GET.get('status')
    export = request.GET.get('export')
    
    samples = Sample.objects.all()
    
    if start_date:
        samples = samples.filter(received_date__gte=start_date)
    if end_date:
        samples = samples.filter(received_date__lte=end_date)
    if sample_type:
        samples = samples.filter(sample_type=sample_type)
    if status:
        samples = samples.filter(status=status)
    
    samples = samples.select_related('assigned_technician', 'registered_by')
    
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sample_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Sample ID', 'Type', 'Source', 'Status', 'Priority', 'Received Date', 'Technician'])
        
        for sample in samples:
            writer.writerow([
                sample.sample_id,
                sample.get_sample_type_display(),
                sample.source,
                sample.get_status_display(),
                sample.get_priority_display(),
                sample.received_date,
                sample.assigned_technician.get_full_name() if sample.assigned_technician else ''
            ])
        
        return response
    
    context = {
        'samples': samples,
        'sample_types': Sample.SAMPLE_TYPE_CHOICES,
        'statuses': Sample.STATUS_CHOICES,
    }
    
    return render(request, 'reports/sample_report.html', context)


@login_required
def test_report(request):
    """Generate test report."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    export = request.GET.get('export')
    
    assignments = TestAssignment.objects.all()
    
    if start_date:
        assignments = assignments.filter(assigned_date__gte=start_date)
    if end_date:
        assignments = assignments.filter(assigned_date__lte=end_date)
    if status:
        assignments = assignments.filter(status=status)
    
    assignments = assignments.select_related('sample', 'test', 'assigned_to')
    
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="test_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Sample ID', 'Test', 'Status', 'Assigned To', 'Assigned Date', 'Completed Date'])
        
        for assignment in assignments:
            writer.writerow([
                assignment.sample.sample_id,
                assignment.test.name,
                assignment.get_status_display(),
                assignment.assigned_to.get_full_name() if assignment.assigned_to else '',
                assignment.assigned_date,
                assignment.completed_date or ''
            ])
        
        return response
    
    context = {
        'assignments': assignments,
        'statuses': TestAssignment.STATUS_CHOICES,
    }
    
    return render(request, 'reports/test_report.html', context)


@login_required
def inventory_report(request):
    """Generate inventory report."""
    export = request.GET.get('export')
    
    reagents = Reagent.objects.all()
    stock_items = StockItem.objects.all()
    
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Type', 'Name', 'Code/Catalog', 'Quantity', 'Unit', 'Min Quantity', 'Status'])
        
        for reagent in reagents:
            status = 'Low Stock' if reagent.is_low_stock else 'OK'
            if reagent.is_expiring_soon:
                status += ' / Expiring Soon'
            writer.writerow([
                'Reagent',
                reagent.name,
                reagent.catalog_number,
                reagent.quantity,
                reagent.unit,
                reagent.minimum_quantity,
                status
            ])
        
        for item in stock_items:
            status = 'Low Stock' if item.is_low_stock else 'OK'
            writer.writerow([
                'Stock Item',
                item.name,
                item.item_code,
                item.quantity,
                item.unit,
                item.minimum_quantity,
                status
            ])
        
        return response
    
    context = {
        'reagents': reagents,
        'stock_items': stock_items,
    }
    
    return render(request, 'reports/inventory_report.html', context)


@login_required
def instrument_report(request):
    """Generate instrument report."""
    export = request.GET.get('export')
    
    instruments = Instrument.objects.all()
    
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="instrument_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Model', 'Serial Number', 'Status', 'Location', 'Last Calibration', 'Next Calibration'])
        
        for instrument in instruments:
            writer.writerow([
                instrument.name,
                instrument.model,
                instrument.serial_number,
                instrument.get_status_display(),
                instrument.location,
                instrument.last_calibration_date or '',
                instrument.next_calibration_date or ''
            ])
        
        return response
    
    context = {
        'instruments': instruments,
    }
    
    return render(request, 'reports/instrument_report.html', context)
