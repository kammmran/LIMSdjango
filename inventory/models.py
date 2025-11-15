from django.db import models
from django.conf import settings


class Reagent(models.Model):
    """Reagents and chemicals inventory."""
    name = models.CharField(max_length=200)
    catalog_number = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=200)
    lot_number = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    storage_location = models.CharField(max_length=200)
    hazard_class = models.CharField(max_length=100, blank=True)
    
    # Cost Management fields
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    help_text='Cost per unit')
    currency = models.CharField(max_length=10, default='USD')
    purchase_date = models.DateField(null=True, blank=True)
    supplier = models.CharField(max_length=200, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.catalog_number})"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_quantity
    
    @property
    def is_expiring_soon(self):
        from datetime import date, timedelta
        return self.expiry_date <= date.today() + timedelta(days=30)
    
    @property
    def total_value(self):
        """Calculate total inventory value for this reagent."""
        if self.unit_cost:
            return self.quantity * self.unit_cost
        return 0
    
    def calculate_consumption_cost(self, quantity_used):
        """Calculate cost for a specific quantity used."""
        if self.unit_cost:
            return quantity_used * self.unit_cost
        return 0
    
    class Meta:
        db_table = 'reagents'
        ordering = ['name']


class StockItem(models.Model):
    """General stock items (consumables, supplies, etc.)."""
    name = models.CharField(max_length=200)
    item_code = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)
    minimum_quantity = models.IntegerField()
    supplier = models.CharField(max_length=200, blank=True)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.item_code})"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_quantity
    
    @property
    def total_value(self):
        """Calculate total inventory value for this stock item."""
        if self.cost_per_unit:
            return self.quantity * self.cost_per_unit
        return 0
    
    class Meta:
        db_table = 'stock_items'
        ordering = ['name']


class InventoryTransaction(models.Model):
    """Track inventory movements."""
    TRANSACTION_TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    reagent = models.ForeignKey(Reagent, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Cost tracking
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    help_text='Cost per unit at time of transaction')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                     help_text='Total cost for this transaction')
    
    reason = models.CharField(max_length=500)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        item = self.reagent or self.stock_item
        return f"{self.get_transaction_type_display()} - {item} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate total cost if not provided."""
        if self.unit_cost and not self.total_cost:
            self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'inventory_transactions'
        ordering = ['-transaction_date']


class CostCenter(models.Model):
    """Cost centers for budget management."""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    yearly_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_monthly_spending(self, year, month):
        """Calculate total spending for a specific month."""
        from datetime import datetime
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        total = self.cost_allocations.filter(
            transaction__transaction_date__gte=start_date,
            transaction__transaction_date__lt=end_date
        ).aggregate(models.Sum('allocated_cost'))['allocated_cost__sum'] or 0
        
        return total
    
    def get_yearly_spending(self, year):
        """Calculate total spending for a specific year."""
        from datetime import datetime
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        
        total = self.cost_allocations.filter(
            transaction__transaction_date__gte=start_date,
            transaction__transaction_date__lt=end_date
        ).aggregate(models.Sum('allocated_cost'))['allocated_cost__sum'] or 0
        
        return total
    
    class Meta:
        db_table = 'cost_centers'
        ordering = ['code']


class CostAllocation(models.Model):
    """Allocate transaction costs to cost centers."""
    transaction = models.ForeignKey(InventoryTransaction, on_delete=models.CASCADE, related_name='cost_allocations')
    cost_center = models.ForeignKey(CostCenter, on_delete=models.CASCADE, related_name='cost_allocations')
    allocated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                    help_text='Percentage of total cost allocated to this center')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.cost_center.code} - {self.allocated_cost}"
    
    class Meta:
        db_table = 'cost_allocations'
        ordering = ['-created_at']
