from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import Reagent, StockItem, InventoryTransaction


@login_required
def inventory_dashboard(request):
    """Inventory dashboard with key metrics."""
    low_stock_reagents = Reagent.objects.filter(quantity__lte=models.F('minimum_quantity')).count()
    low_stock_items = StockItem.objects.filter(quantity__lte=models.F('minimum_quantity')).count()
    expiring_soon = Reagent.objects.filter(
        expiry_date__lte=date.today() + timedelta(days=30)
    ).count()
    
    context = {
        'low_stock_reagents': low_stock_reagents,
        'low_stock_items': low_stock_items,
        'expiring_soon': expiring_soon,
        'total_low_stock': low_stock_reagents + low_stock_items,
    }
    
    return render(request, 'inventory/dashboard.html', context)


@login_required
def reagent_list(request):
    """List all reagents."""
    reagents = Reagent.objects.all()
    
    # Filters
    search = request.GET.get('search', '')
    if search:
        from django.db.models import Q
        reagents = reagents.filter(
            Q(name__icontains=search) |
            Q(catalog_number__icontains=search) |
            Q(manufacturer__icontains=search)
        )
    
    return render(request, 'inventory/reagent_list.html', {'reagents': reagents})


@login_required
def reagent_create(request):
    """Create new reagent."""
    if request.method == 'POST':
        reagent = Reagent.objects.create(
            name=request.POST['name'],
            catalog_number=request.POST['catalog_number'],
            manufacturer=request.POST['manufacturer'],
            lot_number=request.POST['lot_number'],
            quantity=request.POST['quantity'],
            unit=request.POST['unit'],
            minimum_quantity=request.POST['minimum_quantity'],
            expiry_date=request.POST['expiry_date'],
            storage_location=request.POST['storage_location'],
            hazard_class=request.POST.get('hazard_class', ''),
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Reagent added successfully.')
        return redirect('inventory:reagent_list')
    
    return render(request, 'inventory/reagent_form.html', {'action': 'Create'})


@login_required
def reagent_edit(request, pk):
    """Edit reagent."""
    reagent = get_object_or_404(Reagent, pk=pk)
    
    if request.method == 'POST':
        reagent.name = request.POST['name']
        reagent.catalog_number = request.POST['catalog_number']
        reagent.manufacturer = request.POST['manufacturer']
        reagent.lot_number = request.POST['lot_number']
        reagent.quantity = request.POST['quantity']
        reagent.unit = request.POST['unit']
        reagent.minimum_quantity = request.POST['minimum_quantity']
        reagent.expiry_date = request.POST['expiry_date']
        reagent.storage_location = request.POST['storage_location']
        reagent.hazard_class = request.POST.get('hazard_class', '')
        reagent.notes = request.POST.get('notes', '')
        reagent.save()
        messages.success(request, 'Reagent updated successfully.')
        return redirect('inventory:reagent_list')
    
    return render(request, 'inventory/reagent_form.html', {'reagent': reagent, 'action': 'Edit'})


@login_required
def stock_list(request):
    """List all stock items."""
    items = StockItem.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        from django.db.models import Q
        items = items.filter(
            Q(name__icontains=search) |
            Q(item_code__icontains=search) |
            Q(category__icontains=search)
        )
    
    return render(request, 'inventory/stock_list.html', {'items': items})


@login_required
def stock_create(request):
    """Create new stock item."""
    if request.method == 'POST':
        item = StockItem.objects.create(
            name=request.POST['name'],
            item_code=request.POST['item_code'],
            category=request.POST['category'],
            quantity=request.POST['quantity'],
            unit=request.POST['unit'],
            minimum_quantity=request.POST['minimum_quantity'],
            supplier=request.POST.get('supplier', ''),
            cost_per_unit=request.POST.get('cost_per_unit') or None,
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Stock item added successfully.')
        return redirect('inventory:stock_list')
    
    return render(request, 'inventory/stock_form.html', {'action': 'Create'})


@login_required
def stock_edit(request, pk):
    """Edit stock item."""
    item = get_object_or_404(StockItem, pk=pk)
    
    if request.method == 'POST':
        item.name = request.POST['name']
        item.item_code = request.POST['item_code']
        item.category = request.POST['category']
        item.quantity = request.POST['quantity']
        item.unit = request.POST['unit']
        item.minimum_quantity = request.POST['minimum_quantity']
        item.supplier = request.POST.get('supplier', '')
        item.cost_per_unit = request.POST.get('cost_per_unit') or None
        item.notes = request.POST.get('notes', '')
        item.save()
        messages.success(request, 'Stock item updated successfully.')
        return redirect('inventory:stock_list')
    
    return render(request, 'inventory/stock_form.html', {'item': item, 'action': 'Edit'})


@login_required
def transaction_list(request):
    """List inventory transactions."""
    transactions = InventoryTransaction.objects.select_related(
        'reagent', 'stock_item', 'performed_by'
    ).order_by('-transaction_date')[:100]
    
    return render(request, 'inventory/transaction_list.html', {'transactions': transactions})


@login_required
def low_stock_alerts(request):
    """Show low stock and expiring items."""
    from django.db.models import F
    
    low_reagents = Reagent.objects.filter(quantity__lte=F('minimum_quantity'))
    low_stock = StockItem.objects.filter(quantity__lte=F('minimum_quantity'))
    expiring = Reagent.objects.filter(
        expiry_date__lte=date.today() + timedelta(days=30)
    ).order_by('expiry_date')
    
    context = {
        'low_reagents': low_reagents,
        'low_stock': low_stock,
        'expiring': expiring,
    }
    
    return render(request, 'inventory/low_stock_alerts.html', context)
