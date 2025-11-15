# Quick Reference Guide - Cost and Time Management

## Quick Start Commands

### Apply Database Migrations
```bash
# After Django is installed, run:
python manage.py makemigrations
python manage.py migrate
```

---

## Cost Management Quick Reference

### 1. Track Reagent Costs When Purchasing
```python
from inventory.models import Reagent

reagent = Reagent.objects.create(
    name="EDTA Solution",
    catalog_number="EDTA-500",
    manufacturer="ChemCo",
    lot_number="LOT2025A",
    quantity=500,
    unit="mL",
    minimum_quantity=50,
    expiry_date="2026-12-31",
    storage_location="Cabinet A-3",
    # Cost tracking
    unit_cost=2.50,
    currency="USD",
    purchase_date="2025-11-15",
    supplier="Scientific Supplies Inc"
)

print(f"Total value: ${reagent.total_value}")
```

### 2. Record Inventory Transaction with Cost
```python
from inventory.models import InventoryTransaction

transaction = InventoryTransaction.objects.create(
    transaction_type='in',
    reagent=reagent,
    quantity=100,
    unit_cost=2.50,
    # total_cost will be auto-calculated as 250.00
    reason='New stock received',
    performed_by=user
)
```

### 3. Record Test Reagent Usage (Recommended Method)
```python
from tests.utils import record_reagent_usage

usage = record_reagent_usage(
    test_assignment=test_assignment,
    reagent=reagent,
    quantity_used=5.0,
    user=request.user,
    notes='Standard CBC protocol'
)
# This automatically:
# - Records the usage with cost
# - Creates inventory transaction
# - Reduces reagent stock
# - Updates test actual_cost
```

### 4. Set Up Cost Centers
```python
from inventory.models import CostCenter

lab_dept = CostCenter.objects.create(
    name="Laboratory Department",
    code="LAB-001",
    monthly_budget=50000,
    yearly_budget=600000,
    manager=manager_user,
    is_active=True
)
```

### 5. Allocate Costs to Departments
```python
from inventory.utils import allocate_transaction_cost

# Split cost 60/40 between two departments
allocations = allocate_transaction_cost(
    transaction,
    [(lab_dept, 60), (research_dept, 40)]
)
```

### 6. Check Budget Status
```python
from inventory.utils import get_cost_center_budget_status

status = get_cost_center_budget_status(lab_dept, 2025, 11)
print(f"Budget: ${status['monthly']['budget']}")
print(f"Spent: ${status['monthly']['spent']}")
print(f"Remaining: ${status['monthly']['remaining']}")
print(f"Used: {status['monthly']['percentage_used']:.1f}%")
```

### 7. Generate Cost Reports
```python
from tests.utils import get_test_cost_report, get_cost_per_sample_report
from datetime import date

# Test cost report
report = get_test_cost_report(
    test,
    start_date=date(2025, 11, 1),
    end_date=date(2025, 11, 30)
)

# Sample cost report
sample_report = get_cost_per_sample_report(
    start_date=date(2025, 11, 1),
    end_date=date(2025, 11, 30)
)
```

---

## Time Management Quick Reference

### 1. Create Sample with Deadline
```python
from samples.models import Sample
from samples.utils import set_sample_deadline
from django.utils import timezone
from datetime import timedelta

sample = Sample.objects.create(
    sample_type='blood',
    source='Patient John Doe',
    priority='urgent',
    registered_by=user
)

# Auto-set deadline based on priority (urgent = 4 hours)
set_sample_deadline(sample)

# Or set specific deadline
deadline = timezone.now() + timedelta(hours=48)
set_sample_deadline(sample, deadline_datetime=deadline)

# Or set hours from now
set_sample_deadline(sample, deadline_hours=24)
```

### 2. Assign Test with Auto Deadline
```python
from tests.models import TestAssignment

assignment = TestAssignment.objects.create(
    sample=sample,
    test=test,
    assigned_to=technician,
    assigned_by=manager
)
# expected_completion is automatically set based on test.turnaround_time
```

### 3. Check for Overdue Items
```python
from samples.utils import get_overdue_samples, get_overdue_tests

# Get all overdue samples
overdue_samples = get_overdue_samples()
print(f"Overdue samples: {overdue_samples.count()}")

# Get all overdue tests
overdue_tests = get_overdue_tests()
print(f"Overdue tests: {overdue_tests.count()}")
```

### 4. Check Approaching Deadlines
```python
from samples.utils import get_samples_deadline_approaching, get_tests_deadline_approaching

# Samples due in next 24 hours
approaching_samples = get_samples_deadline_approaching(hours=24)

# Tests due in next 12 hours
approaching_tests = get_tests_deadline_approaching(hours=12)
```

### 5. Check Technician Workload
```python
from samples.utils import get_technician_workload

workload = get_technician_workload(technician)

print(f"Total samples: {workload['total_samples']}")
print(f"Total tests: {workload['total_tests']}")
print(f"Overdue samples: {workload['overdue_samples']}")
print(f"Overdue tests: {workload['overdue_tests']}")
print(f"Due today: {workload['due_today_samples']}")
```

### 6. Get Workload Report for Period
```python
from samples.utils import get_sample_workload_report
from datetime import datetime, timedelta

report = get_sample_workload_report(
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=7)
)

print(f"Samples in next 7 days: {report['total_samples']}")
print(f"Tests in next 7 days: {report['total_tests']}")
print(f"Currently overdue: {report['overdue_samples']}")
```

### 7. Mark Sample as Completed
```python
from django.utils import timezone

sample.status = 'completed'
sample.actual_completion_date = timezone.now()
sample.save()
```

---

## Django Admin Quick Access

### View Cost Information
1. Navigate to **Inventory → Reagents**
   - See unit_cost and total_value columns
   - Edit to add supplier and purchase information

2. Navigate to **Inventory → Cost Centers**
   - Create and manage cost centers
   - Set budgets
   - Assign managers

3. Navigate to **Inventory → Inventory Transactions**
   - See unit_cost and total_cost for each transaction

4. Navigate to **Tests → Test Assignments**
   - View actual_cost column
   - See reagent usages inline

### View Time Information
1. Navigate to **Samples → Samples**
   - See completion_deadline column
   - See is_overdue status
   - Edit to set deadlines

2. Navigate to **Tests → Test Assignments**
   - See deadline and expected_completion
   - See is_overdue status
   - See time_remaining

---

## Dashboard Widget Ideas

### Cost Dashboard Widgets
```python
# Total inventory value
from inventory.utils import calculate_total_inventory_value
total_value = calculate_total_inventory_value()

# Monthly costs
from inventory.utils import get_monthly_costs
costs = get_monthly_costs(2025, 11)

# Low stock alerts (includes cost impact)
from inventory.utils import get_low_stock_alerts
alerts = get_low_stock_alerts()
```

### Time Dashboard Widgets
```python
# Overdue counters
overdue_samples_count = get_overdue_samples().count()
overdue_tests_count = get_overdue_tests().count()

# Due today
from django.utils import timezone
now = timezone.now()
end_of_day = now.replace(hour=23, minute=59, second=59)

due_today_samples = Sample.objects.filter(
    completion_deadline__gte=now,
    completion_deadline__lte=end_of_day
).exclude(status__in=['completed', 'archived']).count()
```

---

## Common Workflows

### Complete Workflow: Sample with Tests and Costs

```python
from django.utils import timezone
from datetime import timedelta
from samples.models import Sample
from samples.utils import set_sample_deadline
from tests.models import Test, TestAssignment
from tests.utils import record_reagent_usage
from inventory.models import Reagent

# 1. Register sample with deadline
sample = Sample.objects.create(
    sample_type='blood',
    source='Patient ABC',
    priority='high',
    registered_by=user
)
set_sample_deadline(sample)  # Auto-set based on priority

# 2. Assign tests
cbc_test = Test.objects.get(code='CBC')
assignment = TestAssignment.objects.create(
    sample=sample,
    test=cbc_test,
    assigned_to=technician,
    assigned_by=user
)
# Deadline auto-set from turnaround time

# 3. Perform test and record reagent usage
edta = Reagent.objects.get(catalog_number='EDTA-500')
heparin = Reagent.objects.get(catalog_number='HEP-100')

record_reagent_usage(assignment, edta, 2.5, user)
record_reagent_usage(assignment, heparin, 1.0, user)
# Costs automatically calculated and tracked

# 4. Complete test
assignment.status = 'completed'
assignment.completed_date = timezone.now()
assignment.save()

# 5. Complete sample
if all(t.status == 'completed' for t in sample.test_assignments.all()):
    sample.status = 'completed'
    sample.actual_completion_date = timezone.now()
    sample.save()

# 6. Check costs
from tests.utils import get_sample_total_cost
total_cost = get_sample_total_cost(sample)
print(f"Total sample cost: ${total_cost}")
```

---

## Scheduled Tasks (Cron Jobs / Celery)

### Daily Tasks
```python
# Send deadline alerts
def daily_deadline_alerts():
    # Samples due today
    samples = get_samples_deadline_approaching(hours=24)
    # Send notifications...
    
    # Overdue items
    overdue = get_overdue_samples()
    # Send escalation notifications...

# Check budget status
def daily_budget_check():
    for cost_center in CostCenter.objects.filter(is_active=True):
        status = get_cost_center_budget_status(cost_center)
        if status['monthly']['percentage_used'] > 90:
            # Send warning...
            pass
```

### Weekly Tasks
```python
# Generate cost reports
def weekly_cost_reports():
    from datetime import date, timedelta
    end = date.today()
    start = end - timedelta(days=7)
    
    # Generate reports for each test type
    for test in Test.objects.filter(is_active=True):
        report = get_test_cost_report(test, start, end)
        # Email report to managers...

# Update estimated costs
def weekly_cost_update():
    from tests.utils import update_test_estimated_costs
    updated = update_test_estimated_costs()
    print(f"Updated {updated} test cost estimates")
```

---

## Integration with Views

### Example View with Cost and Time Info
```python
from django.shortcuts import render
from samples.utils import get_technician_workload
from inventory.utils import get_cost_center_budget_status

def dashboard_view(request):
    # Time management data
    workload = get_technician_workload(request.user)
    
    # Cost management data
    if hasattr(request.user, 'cost_center'):
        budget_status = get_cost_center_budget_status(
            request.user.cost_center
        )
    else:
        budget_status = None
    
    context = {
        'workload': workload,
        'budget_status': budget_status,
    }
    
    return render(request, 'dashboard/home.html', context)
```

---

## Troubleshooting

### Cost Not Calculating?
- Ensure `unit_cost` is set on reagent
- Check that `quantity_used` is provided
- Verify `save()` method is called

### Deadline Not Auto-Setting?
- Ensure `turnaround_time` is set on Test model
- Check that sample has a `priority` set
- Verify timezone is configured in settings

### Budget Overspending?
- Check cost allocations are correct
- Verify transactions are properly recorded
- Review cost center budget amounts

---

## Next Steps

1. **Apply migrations**: `python manage.py migrate`
2. **Create cost centers** in admin interface
3. **Update existing reagents** with cost information
4. **Set up test costs** (estimated and billable)
5. **Configure deadlines** for existing samples
6. **Start recording reagent usage** for new tests
7. **Create dashboard views** with widgets
8. **Set up automated reports** and alerts
