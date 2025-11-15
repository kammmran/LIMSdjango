# Cost and Time Management Features

This document describes the cost management and time management features added to the LIMS system.

## Table of Contents
1. [Cost Management](#cost-management)
2. [Time Management](#time-management)
3. [Usage Examples](#usage-examples)
4. [Database Changes](#database-changes)

---

## Cost Management

### Overview
The system now tracks costs for reagents, stock items, tests, and provides budget management through cost centers.

### Features

#### 1. Reagent Cost Tracking
**New Fields in Reagent Model:**
- `unit_cost`: Cost per unit of the reagent
- `currency`: Currency code (default: USD)
- `purchase_date`: Date of purchase
- `supplier`: Supplier name

**Properties and Methods:**
- `total_value`: Automatically calculates total inventory value (quantity × unit_cost)
- `calculate_consumption_cost(quantity_used)`: Calculate cost for specific quantity used

#### 2. Inventory Transaction Cost Tracking
**New Fields in InventoryTransaction Model:**
- `unit_cost`: Cost per unit at time of transaction
- `total_cost`: Total cost for the transaction (auto-calculated)

**Auto-calculation:**
The `total_cost` is automatically calculated when saving if not provided: `quantity × unit_cost`

#### 3. Stock Item Cost Tracking
**Existing Field Enhanced:**
- `cost_per_unit`: Cost per unit of stock item

**New Property:**
- `total_value`: Calculates total inventory value

#### 4. Cost Centers and Budget Management
**New Model: CostCenter**
Track organizational cost centers with budget limits:
- `name`, `code`: Identifier
- `monthly_budget`: Monthly budget limit
- `yearly_budget`: Yearly budget limit
- `manager`: Responsible person
- `is_active`: Whether cost center is active

**Methods:**
- `get_monthly_spending(year, month)`: Get total spending for a month
- `get_yearly_spending(year)`: Get total spending for a year

**New Model: CostAllocation**
Allocate transaction costs to cost centers:
- `transaction`: Related inventory transaction
- `cost_center`: Associated cost center
- `allocated_cost`: Amount allocated
- `percentage`: Percentage of total cost

#### 5. Test Cost Tracking
**New Fields in Test Model:**
- `estimated_cost`: Estimated cost per test
- `billable_amount`: Amount charged to client

**New Fields in TestAssignment Model:**
- `actual_cost`: Actual cost incurred (calculated from reagent usage)

**New Model: ReagentUsage**
Track reagent usage per test:
- `test_assignment`: Related test
- `reagent`: Reagent used
- `quantity_used`: Quantity consumed
- `unit_cost_at_usage`: Cost at time of use
- `total_cost`: Auto-calculated total cost
- `used_by`, `used_date`: Tracking information

### Utility Functions for Cost Management

#### `inventory/utils.py`

1. **`calculate_total_inventory_value()`**
   - Returns total value of all inventory

2. **`get_monthly_costs(year, month, cost_center=None)`**
   - Get cost breakdown for a specific month
   - Optional cost center filtering

3. **`get_reagent_consumption_report(reagent, start_date, end_date)`**
   - Generate consumption statistics for a reagent
   - Includes consumption rate and days remaining

4. **`allocate_transaction_cost(transaction, cost_center_allocations)`**
   - Allocate transaction costs to cost centers
   - Example: `[(cost_center1, 60), (cost_center2, 40)]`

5. **`get_cost_center_budget_status(cost_center, year, month)`**
   - Compare budget vs actual spending
   - Returns monthly and yearly status

#### `tests/utils.py`

1. **`record_reagent_usage(test_assignment, reagent, quantity_used, user, notes)`**
   - Record reagent usage for a test
   - Creates inventory transaction
   - Updates reagent stock
   - Recalculates test cost

2. **`calculate_test_assignment_cost(test_assignment)`**
   - Calculate total cost from reagent usages
   - Updates `actual_cost` field

3. **`get_test_cost_report(test, start_date, end_date)`**
   - Generate cost report for a test type
   - Includes estimated vs actual variance
   - Calculates profit if billable

4. **`get_sample_total_cost(sample)`**
   - Calculate total cost for all tests on a sample

5. **`get_reagent_test_usage_report(reagent, start_date, end_date)`**
   - Show which tests use a specific reagent
   - Breakdown by test type

6. **`get_cost_per_sample_report(start_date, end_date)`**
   - Report costs per sample
   - Sort by total cost

7. **`update_test_estimated_costs()`**
   - Update estimated costs based on historical data

---

## Time Management

### Overview
Track deadlines and turnaround times for samples and tests.

### Features

#### 1. Sample Deadline Tracking
**New Fields in Sample Model:**
- `expected_completion_date`: Expected completion (date only)
- `completion_deadline`: Hard deadline (datetime)
- `actual_completion_date`: When actually completed

**Properties:**
- `is_overdue`: Check if past deadline and not completed
- `is_deadline_approaching(hours=24)`: Check if deadline within specified hours
- `days_until_deadline`: Days remaining until deadline

#### 2. Test Assignment Deadline Tracking
**New Fields in TestAssignment Model:**
- `expected_completion`: Expected completion based on turnaround time
- `deadline`: Hard deadline for test completion

**Properties:**
- `is_overdue`: Check if past deadline
- `is_deadline_approaching(hours=12)`: Check if deadline within specified hours
- `time_remaining`: Time delta until deadline

**Auto-calculation:**
When a TestAssignment is created, `expected_completion` is automatically calculated:
```python
expected_completion = now + timedelta(hours=test.turnaround_time)
```

### Utility Functions for Time Management

#### `samples/utils.py`

1. **`get_overdue_samples()`**
   - Get all samples past their deadline

2. **`get_samples_deadline_approaching(hours=24)`**
   - Get samples with approaching deadlines

3. **`get_overdue_tests()`**
   - Get all test assignments past deadline

4. **`get_tests_deadline_approaching(hours=12)`**
   - Get test assignments with approaching deadlines

5. **`set_sample_deadline(sample, deadline_hours, deadline_datetime)`**
   - Set deadline for a sample
   - Can specify hours from now or specific datetime
   - Auto-sets based on priority if neither specified:
     - Urgent: 4 hours
     - High: 24 hours
     - Normal: 72 hours
     - Low: 168 hours (1 week)

6. **`set_test_deadline(test_assignment)`**
   - Set deadline based on test turnaround time

7. **`calculate_expected_completion(sample)`**
   - Calculate when sample will be complete
   - Based on latest test completion time

8. **`get_sample_workload_report(start_date, end_date)`**
   - Get workload statistics for a time period
   - Breakdown by status

9. **`get_technician_workload(technician, include_completed)`**
   - Get workload for a specific technician
   - Shows overdue items and items due today

---

## Usage Examples

### Cost Management Examples

#### Record Reagent Usage for a Test
```python
from tests.utils import record_reagent_usage
from tests.models import TestAssignment
from inventory.models import Reagent

# Get the test assignment and reagent
assignment = TestAssignment.objects.get(id=1)
reagent = Reagent.objects.get(catalog_number='REA-001')

# Record usage
usage = record_reagent_usage(
    test_assignment=assignment,
    reagent=reagent,
    quantity_used=5.0,
    user=request.user,
    notes='Standard protocol'
)

# Cost is automatically calculated and test actual_cost is updated
print(f"Usage cost: {usage.total_cost}")
print(f"Test total cost: {assignment.actual_cost}")
```

#### Allocate Transaction Cost to Cost Centers
```python
from inventory.utils import allocate_transaction_cost
from inventory.models import InventoryTransaction, CostCenter

transaction = InventoryTransaction.objects.get(id=1)
lab_dept = CostCenter.objects.get(code='LAB-001')
research_dept = CostCenter.objects.get(code='RES-001')

# Allocate 70% to lab, 30% to research
allocations = allocate_transaction_cost(
    transaction,
    [(lab_dept, 70), (research_dept, 30)]
)
```

#### Get Cost Center Budget Status
```python
from inventory.utils import get_cost_center_budget_status
from inventory.models import CostCenter

cost_center = CostCenter.objects.get(code='LAB-001')
status = get_cost_center_budget_status(cost_center, 2025, 11)

print(f"Monthly budget: ${status['monthly']['budget']}")
print(f"Monthly spent: ${status['monthly']['spent']}")
print(f"Remaining: ${status['monthly']['remaining']}")
print(f"Percentage used: {status['monthly']['percentage_used']:.1f}%")
```

#### Generate Test Cost Report
```python
from tests.utils import get_test_cost_report
from tests.models import Test
from datetime import date

test = Test.objects.get(code='CBC')
report = get_test_cost_report(
    test,
    start_date=date(2025, 1, 1),
    end_date=date(2025, 11, 15)
)

print(f"Total tests: {report['total_tests_completed']}")
print(f"Average cost: ${report['average_cost_per_test']}")
print(f"Total profit: ${report['total_profit']}")
```

### Time Management Examples

#### Set Sample Deadline Based on Priority
```python
from samples.utils import set_sample_deadline
from samples.models import Sample

sample = Sample.objects.get(sample_id='SMP-20251115-0001')

# Auto-set based on priority
set_sample_deadline(sample)

# Or set specific hours
set_sample_deadline(sample, deadline_hours=48)

# Or set specific datetime
from django.utils import timezone
from datetime import timedelta
deadline = timezone.now() + timedelta(days=2)
set_sample_deadline(sample, deadline_datetime=deadline)
```

#### Check for Overdue Items
```python
from samples.utils import get_overdue_samples, get_overdue_tests

# Get overdue samples
overdue_samples = get_overdue_samples()
for sample in overdue_samples:
    print(f"{sample.sample_id} is {sample.days_until_deadline} days overdue")

# Get overdue tests
overdue_tests = get_overdue_tests()
for test in overdue_tests:
    print(f"{test.sample.sample_id} - {test.test.code} is overdue")
```

#### Get Technician Workload
```python
from samples.utils import get_technician_workload
from django.contrib.auth import get_user_model

User = get_user_model()
technician = User.objects.get(username='tech1')

workload = get_technician_workload(technician)

print(f"Total samples: {workload['total_samples']}")
print(f"Total tests: {workload['total_tests']}")
print(f"Overdue samples: {workload['overdue_samples']}")
print(f"Due today samples: {workload['due_today_samples']}")
```

#### Generate Workload Report
```python
from samples.utils import get_sample_workload_report
from datetime import datetime, timedelta

start = datetime.now()
end = start + timedelta(days=7)

report = get_sample_workload_report(start, end)

print(f"Total samples in next 7 days: {report['total_samples']}")
print(f"Total tests in next 7 days: {report['total_tests']}")
print(f"Currently overdue samples: {report['overdue_samples']}")
print("\nSamples by status:")
for status, count in report['samples_by_status'].items():
    print(f"  {status}: {count}")
```

---

## Database Changes

### Migration Steps

After making these changes, you need to create and apply migrations:

```bash
# Create migrations for all apps
python manage.py makemigrations inventory
python manage.py makemigrations samples
python manage.py makemigrations tests

# Apply migrations
python manage.py migrate
```

### New Database Tables

1. **`cost_centers`** - Cost center definitions
2. **`cost_allocations`** - Transaction cost allocations
3. **`reagent_usages`** - Reagent usage tracking per test

### Modified Tables

1. **`reagents`**
   - Added: `unit_cost`, `currency`, `purchase_date`, `supplier`

2. **`inventory_transactions`**
   - Added: `unit_cost`, `total_cost`

3. **`samples`**
   - Added: `expected_completion_date`, `completion_deadline`, `actual_completion_date`

4. **`tests`**
   - Added: `estimated_cost`, `billable_amount`

5. **`test_assignments`**
   - Added: `expected_completion`, `deadline`, `actual_cost`

---

## Admin Interface Updates

All new fields are accessible through the Django admin interface with:
- Enhanced list displays showing cost and deadline information
- Readonly fields for calculated values
- Organized fieldsets for better data entry
- Inline editing for related records (e.g., ReagentUsage in TestAssignment)

---

## API Integration (Future)

These models and utility functions are ready for REST API integration. You can:
1. Create API endpoints for cost reports
2. Create API endpoints for deadline alerts
3. Integrate with notification systems for approaching deadlines
4. Create dashboards showing budget status

---

## Best Practices

### Cost Management
1. Always record reagent usage when performing tests
2. Regularly update unit costs when purchasing new inventory
3. Review cost center budgets monthly
4. Update test estimated costs based on actual usage

### Time Management
1. Set deadlines when registering samples
2. Regularly check for overdue items
3. Use priority levels to auto-set appropriate deadlines
4. Monitor technician workload to balance assignments

---

## Reporting Dashboard Ideas

You can create dashboards showing:

1. **Cost Dashboard**
   - Total inventory value
   - Monthly spending trends
   - Cost center budget vs actual
   - Most expensive tests
   - Reagent consumption rates

2. **Time Dashboard**
   - Overdue samples/tests
   - Items due today/this week
   - Technician workload distribution
   - Average turnaround times
   - On-time completion rates

---

## Future Enhancements

Possible future additions:
1. Email/SMS notifications for approaching deadlines
2. Automated purchase orders when stock is low
3. Cost variance analysis and alerts
4. Integration with accounting systems
5. Predictive analytics for reagent consumption
6. Automated deadline adjustment based on workload
