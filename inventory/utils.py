"""Utility functions for inventory cost management."""
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Q
from django.utils import timezone


def calculate_total_inventory_value():
    """Calculate total value of all inventory (reagents and stock items)."""
    from inventory.models import Reagent, StockItem
    
    reagent_value = Reagent.objects.aggregate(
        total=Sum('quantity') * Sum('unit_cost')
    )['total'] or Decimal('0.00')
    
    stock_value = StockItem.objects.aggregate(
        total=Sum('quantity') * Sum('cost_per_unit')
    )['total'] or Decimal('0.00')
    
    return reagent_value + stock_value


def get_monthly_costs(year, month, cost_center=None):
    """
    Get total costs for a specific month.
    
    Args:
        year: Year
        month: Month (1-12)
        cost_center: Optional CostCenter instance to filter by
    
    Returns:
        Dictionary with cost breakdown
    """
    from inventory.models import InventoryTransaction, CostAllocation
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Get transactions for the period
    transactions = InventoryTransaction.objects.filter(
        transaction_date__gte=start_date,
        transaction_date__lt=end_date
    )
    
    # Calculate costs
    total_costs = transactions.aggregate(
        total=Sum('total_cost')
    )['total'] or Decimal('0.00')
    
    # Break down by transaction type
    stock_in = transactions.filter(transaction_type='in').aggregate(
        total=Sum('total_cost')
    )['total'] or Decimal('0.00')
    
    stock_out = transactions.filter(transaction_type='out').aggregate(
        total=Sum('total_cost')
    )['total'] or Decimal('0.00')
    
    # Get cost center allocation if specified
    if cost_center:
        allocated = CostAllocation.objects.filter(
            cost_center=cost_center,
            transaction__transaction_date__gte=start_date,
            transaction__transaction_date__lt=end_date
        ).aggregate(
            total=Sum('allocated_cost')
        )['total'] or Decimal('0.00')
    else:
        allocated = None
    
    return {
        'total_costs': total_costs,
        'stock_in_costs': stock_in,
        'stock_out_costs': stock_out,
        'cost_center_allocated': allocated,
        'period': f"{year}-{month:02d}",
    }


def get_reagent_consumption_report(reagent, start_date=None, end_date=None):
    """
    Generate consumption report for a specific reagent.
    
    Args:
        reagent: Reagent instance
        start_date: Optional start date
        end_date: Optional end date
    
    Returns:
        Dictionary with consumption statistics
    """
    from inventory.models import InventoryTransaction
    
    if not start_date:
        start_date = timezone.now() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now()
    
    # Get all outgoing transactions for this reagent
    transactions = InventoryTransaction.objects.filter(
        reagent=reagent,
        transaction_type='out',
        transaction_date__gte=start_date,
        transaction_date__lte=end_date
    )
    
    total_consumed = transactions.aggregate(
        total=Sum('quantity')
    )['total'] or Decimal('0.00')
    
    total_cost = transactions.aggregate(
        total=Sum('total_cost')
    )['total'] or Decimal('0.00')
    
    avg_daily_consumption = total_consumed / max((end_date - start_date).days, 1)
    
    # Calculate days until stock runs out
    if avg_daily_consumption > 0:
        days_remaining = reagent.quantity / avg_daily_consumption
    else:
        days_remaining = None
    
    return {
        'reagent': reagent.name,
        'period_start': start_date,
        'period_end': end_date,
        'total_consumed': total_consumed,
        'total_cost': total_cost,
        'average_daily_consumption': avg_daily_consumption,
        'current_stock': reagent.quantity,
        'estimated_days_remaining': days_remaining,
        'unit_cost': reagent.unit_cost,
    }


def get_low_stock_alerts():
    """Get all reagents and stock items that are low or expiring."""
    from inventory.models import Reagent, StockItem
    from django.db.models import F
    
    low_reagents = Reagent.objects.filter(
        quantity__lte=F('minimum_quantity')
    )
    
    expiring_reagents = [r for r in Reagent.objects.all() if r.is_expiring_soon]
    
    low_stock_items = StockItem.objects.filter(
        quantity__lte=F('minimum_quantity')
    )
    
    return {
        'low_stock_reagents': low_reagents,
        'expiring_reagents': expiring_reagents,
        'low_stock_items': low_stock_items,
    }


def allocate_transaction_cost(transaction, cost_center_allocations):
    """
    Allocate transaction cost to one or more cost centers.
    
    Args:
        transaction: InventoryTransaction instance
        cost_center_allocations: List of tuples (cost_center, percentage)
                                 e.g., [(cost_center1, 60), (cost_center2, 40)]
    """
    from inventory.models import CostAllocation
    
    if not transaction.total_cost:
        raise ValueError("Transaction must have a total cost to allocate")
    
    total_percentage = sum(percentage for _, percentage in cost_center_allocations)
    if abs(total_percentage - 100) > 0.01:
        raise ValueError("Total allocation percentage must equal 100")
    
    allocations = []
    for cost_center, percentage in cost_center_allocations:
        allocated_amount = (transaction.total_cost * Decimal(str(percentage))) / Decimal('100')
        allocation = CostAllocation.objects.create(
            transaction=transaction,
            cost_center=cost_center,
            allocated_cost=allocated_amount,
            percentage=Decimal(str(percentage))
        )
        allocations.append(allocation)
    
    return allocations


def get_cost_center_budget_status(cost_center, year=None, month=None):
    """
    Get budget vs actual spending status for a cost center.
    
    Args:
        cost_center: CostCenter instance
        year: Optional year (defaults to current)
        month: Optional month (defaults to current)
    
    Returns:
        Dictionary with budget status
    """
    if not year:
        year = timezone.now().year
    if not month:
        month = timezone.now().month
    
    monthly_spending = cost_center.get_monthly_spending(year, month)
    yearly_spending = cost_center.get_yearly_spending(year)
    
    monthly_budget = cost_center.monthly_budget or Decimal('0.00')
    yearly_budget = cost_center.yearly_budget or Decimal('0.00')
    
    monthly_remaining = monthly_budget - monthly_spending
    yearly_remaining = yearly_budget - yearly_spending
    
    monthly_percentage = (monthly_spending / monthly_budget * 100) if monthly_budget > 0 else 0
    yearly_percentage = (yearly_spending / yearly_budget * 100) if yearly_budget > 0 else 0
    
    return {
        'cost_center': cost_center.name,
        'monthly': {
            'budget': monthly_budget,
            'spent': monthly_spending,
            'remaining': monthly_remaining,
            'percentage_used': monthly_percentage,
        },
        'yearly': {
            'budget': yearly_budget,
            'spent': yearly_spending,
            'remaining': yearly_remaining,
            'percentage_used': yearly_percentage,
        },
    }
