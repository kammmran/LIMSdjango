#!/usr/bin/env python
"""
Populate the LIMS database with example data for testing and demonstration.
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Role
from samples.models import Sample
from tests.models import Test, TestParameter, TestAssignment
from results.models import TestResult, ParameterResult
from inventory.models import Reagent, StockItem
from instruments.models import Instrument, CalibrationRecord, MaintenanceLog

User = get_user_model()

def create_roles():
    """Create user roles."""
    print("Creating roles...")
    roles_data = [
        {
            'name': 'admin',
            'description': 'Full system access',
            'can_register_samples': True,
            'can_assign_tests': True,
            'can_enter_results': True,
            'can_approve_results': True,
            'can_manage_inventory': True,
            'can_manage_instruments': True,
            'can_view_reports': True,
            'can_manage_users': True,
        },
        {
            'name': 'technician',
            'description': 'Can perform tests and enter results',
            'can_register_samples': True,
            'can_assign_tests': True,
            'can_enter_results': True,
            'can_approve_results': False,
            'can_manage_inventory': True,
            'can_manage_instruments': False,
            'can_view_reports': True,
            'can_manage_users': False,
        },
        {
            'name': 'lab_manager',
            'description': 'Can approve results and manage lab operations',
            'can_register_samples': True,
            'can_assign_tests': True,
            'can_enter_results': True,
            'can_approve_results': True,
            'can_manage_inventory': True,
            'can_manage_instruments': True,
            'can_view_reports': True,
            'can_manage_users': False,
        },
    ]
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults=role_data
        )
        if created:
            print(f"  ✓ Created role: {role.get_name_display()}")


def create_users():
    """Create sample users."""
    print("\nCreating users...")
    
    # Get roles
    admin_role = Role.objects.get(name='admin')
    tech_role = Role.objects.get(name='technician')
    manager_role = Role.objects.get(name='lab_manager')
    
    users_data = [
        # Admin users
        {
            'username': 'admin',
            'email': 'admin@lims.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'employee_id': 'EMP-001',
            'role': admin_role,
            'is_superuser': True,
            'is_staff': True,
        },
        # Lab managers
        {
            'username': 'manager',
            'email': 'manager@lims.com',
            'first_name': 'Michael',
            'last_name': 'Brown',
            'employee_id': 'EMP-002',
            'role': manager_role,
        },
        {
            'username': 'manager2',
            'email': 'manager2@lims.com',
            'first_name': 'Jennifer',
            'last_name': 'Davis',
            'employee_id': 'EMP-003',
            'role': manager_role,
        },
        # Technicians
        {
            'username': 'tech1',
            'email': 'tech1@lims.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'employee_id': 'EMP-004',
            'role': tech_role,
        },
        {
            'username': 'tech2',
            'email': 'tech2@lims.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'employee_id': 'EMP-005',
            'role': tech_role,
        },
        {
            'username': 'tech3',
            'email': 'tech3@lims.com',
            'first_name': 'David',
            'last_name': 'Wilson',
            'employee_id': 'EMP-006',
            'role': tech_role,
        },
        {
            'username': 'tech4',
            'email': 'tech4@lims.com',
            'first_name': 'Emily',
            'last_name': 'Martinez',
            'employee_id': 'EMP-007',
            'role': tech_role,
        },
        {
            'username': 'tech5',
            'email': 'tech5@lims.com',
            'first_name': 'Robert',
            'last_name': 'Anderson',
            'employee_id': 'EMP-008',
            'role': tech_role,
        },
        {
            'username': 'tech6',
            'email': 'tech6@lims.com',
            'first_name': 'Lisa',
            'last_name': 'Taylor',
            'employee_id': 'EMP-009',
            'role': tech_role,
        },
        {
            'username': 'tech7',
            'email': 'tech7@lims.com',
            'first_name': 'James',
            'last_name': 'Thomas',
            'employee_id': 'EMP-010',
            'role': tech_role,
        },
        {
            'username': 'tech8',
            'email': 'tech8@lims.com',
            'first_name': 'Mary',
            'last_name': 'Garcia',
            'employee_id': 'EMP-011',
            'role': tech_role,
        },
    ]
    
    users_created = 0
    for user_data in users_data:
        username = user_data.pop('username')
        user, created = User.objects.get_or_create(
            username=username,
            defaults=user_data
        )
        if created:
            user.set_password('password123')
            user.save()
            users_created += 1
    
    print(f"  ✓ Created {users_created} users (all passwords: password123)")


def create_tests():
    """Create test types with parameters."""
    print("\nCreating test types...")
    
    tests_data = [
        # Hematology Tests
        {
            'name': 'Complete Blood Count',
            'code': 'CBC',
            'category': 'hematology',
            'description': 'Comprehensive blood analysis',
            'turnaround_time': 24,
            'parameters': [
                {'name': 'WBC', 'unit': '10^9/L', 'range': '4.0-11.0'},
                {'name': 'RBC', 'unit': '10^12/L', 'range': '4.5-5.5'},
                {'name': 'Hemoglobin', 'unit': 'g/dL', 'range': '12.0-16.0'},
                {'name': 'Hematocrit', 'unit': '%', 'range': '36-46'},
                {'name': 'Platelets', 'unit': '10^9/L', 'range': '150-400'},
                {'name': 'MCV', 'unit': 'fL', 'range': '80-100'},
                {'name': 'MCH', 'unit': 'pg', 'range': '27-32'},
                {'name': 'MCHC', 'unit': 'g/dL', 'range': '32-36'},
            ]
        },
        {
            'name': 'Differential Count',
            'code': 'DIFF',
            'category': 'hematology',
            'description': 'White blood cell differential',
            'turnaround_time': 12,
            'parameters': [
                {'name': 'Neutrophils', 'unit': '%', 'range': '40-70'},
                {'name': 'Lymphocytes', 'unit': '%', 'range': '20-40'},
                {'name': 'Monocytes', 'unit': '%', 'range': '2-8'},
                {'name': 'Eosinophils', 'unit': '%', 'range': '1-4'},
                {'name': 'Basophils', 'unit': '%', 'range': '0-1'},
            ]
        },
        {
            'name': 'ESR',
            'code': 'ESR',
            'category': 'hematology',
            'description': 'Erythrocyte Sedimentation Rate',
            'turnaround_time': 6,
            'parameters': [
                {'name': 'ESR', 'unit': 'mm/hr', 'range': '0-20'},
            ]
        },
        {
            'name': 'Reticulocyte Count',
            'code': 'RETIC',
            'category': 'hematology',
            'description': 'Reticulocyte count',
            'turnaround_time': 12,
            'parameters': [
                {'name': 'Reticulocytes', 'unit': '%', 'range': '0.5-2.5'},
            ]
        },
        
        # Biochemistry Tests
        {
            'name': 'Liver Function Test',
            'code': 'LFT',
            'category': 'biochemistry',
            'description': 'Liver enzyme and function tests',
            'turnaround_time': 12,
            'parameters': [
                {'name': 'ALT', 'unit': 'U/L', 'range': '7-56'},
                {'name': 'AST', 'unit': 'U/L', 'range': '10-40'},
                {'name': 'ALP', 'unit': 'U/L', 'range': '44-147'},
                {'name': 'Total Bilirubin', 'unit': 'mg/dL', 'range': '0.1-1.2'},
                {'name': 'Direct Bilirubin', 'unit': 'mg/dL', 'range': '0-0.3'},
                {'name': 'Albumin', 'unit': 'g/dL', 'range': '3.5-5.5'},
                {'name': 'Total Protein', 'unit': 'g/dL', 'range': '6.0-8.3'},
                {'name': 'GGT', 'unit': 'U/L', 'range': '8-61'},
            ]
        },
        {
            'name': 'Renal Function Test',
            'code': 'RFT',
            'category': 'biochemistry',
            'description': 'Kidney function assessment',
            'turnaround_time': 12,
            'parameters': [
                {'name': 'Creatinine', 'unit': 'mg/dL', 'range': '0.6-1.2'},
                {'name': 'BUN', 'unit': 'mg/dL', 'range': '7-20'},
                {'name': 'Uric Acid', 'unit': 'mg/dL', 'range': '3.5-7.2'},
                {'name': 'Sodium', 'unit': 'mmol/L', 'range': '136-145'},
                {'name': 'Potassium', 'unit': 'mmol/L', 'range': '3.5-5.0'},
                {'name': 'Chloride', 'unit': 'mmol/L', 'range': '98-107'},
                {'name': 'Bicarbonate', 'unit': 'mmol/L', 'range': '22-29'},
            ]
        },
        {
            'name': 'Lipid Profile',
            'code': 'LIPID',
            'category': 'biochemistry',
            'description': 'Cholesterol and triglyceride analysis',
            'turnaround_time': 24,
            'parameters': [
                {'name': 'Total Cholesterol', 'unit': 'mg/dL', 'range': '<200'},
                {'name': 'HDL', 'unit': 'mg/dL', 'range': '>40'},
                {'name': 'LDL', 'unit': 'mg/dL', 'range': '<100'},
                {'name': 'Triglycerides', 'unit': 'mg/dL', 'range': '<150'},
                {'name': 'VLDL', 'unit': 'mg/dL', 'range': '5-40'},
            ]
        },
        {
            'name': 'Blood Glucose',
            'code': 'GLU',
            'category': 'biochemistry',
            'description': 'Blood sugar test',
            'turnaround_time': 6,
            'parameters': [
                {'name': 'Glucose', 'unit': 'mg/dL', 'range': '70-100'},
            ]
        },
        {
            'name': 'HbA1c',
            'code': 'HBA1C',
            'category': 'biochemistry',
            'description': 'Glycated Hemoglobin',
            'turnaround_time': 24,
            'parameters': [
                {'name': 'HbA1c', 'unit': '%', 'range': '4.0-5.6'},
            ]
        },
        {
            'name': 'Thyroid Function Test',
            'code': 'TFT',
            'category': 'biochemistry',
            'description': 'Thyroid hormone levels',
            'turnaround_time': 48,
            'parameters': [
                {'name': 'TSH', 'unit': 'mIU/L', 'range': '0.4-4.0'},
                {'name': 'T3', 'unit': 'ng/dL', 'range': '80-200'},
                {'name': 'T4', 'unit': 'μg/dL', 'range': '4.5-12.0'},
                {'name': 'Free T4', 'unit': 'ng/dL', 'range': '0.8-1.8'},
            ]
        },
        {
            'name': 'Electrolytes Panel',
            'code': 'ELEC',
            'category': 'biochemistry',
            'description': 'Electrolyte balance',
            'turnaround_time': 6,
            'parameters': [
                {'name': 'Sodium', 'unit': 'mmol/L', 'range': '136-145'},
                {'name': 'Potassium', 'unit': 'mmol/L', 'range': '3.5-5.0'},
                {'name': 'Chloride', 'unit': 'mmol/L', 'range': '98-107'},
                {'name': 'Calcium', 'unit': 'mg/dL', 'range': '8.5-10.5'},
                {'name': 'Magnesium', 'unit': 'mg/dL', 'range': '1.7-2.2'},
            ]
        },
        {
            'name': 'Cardiac Markers',
            'code': 'CARDIAC',
            'category': 'biochemistry',
            'description': 'Heart damage markers',
            'turnaround_time': 4,
            'parameters': [
                {'name': 'Troponin I', 'unit': 'ng/mL', 'range': '<0.04'},
                {'name': 'CK-MB', 'unit': 'U/L', 'range': '<25'},
                {'name': 'Myoglobin', 'unit': 'ng/mL', 'range': '<90'},
            ]
        },
        
        # Microbiology Tests
        {
            'name': 'Urinalysis',
            'code': 'UA',
            'category': 'microbiology',
            'description': 'Urine analysis',
            'turnaround_time': 12,
            'parameters': [
                {'name': 'Color', 'unit': '', 'range': 'Yellow'},
                {'name': 'Appearance', 'unit': '', 'range': 'Clear'},
                {'name': 'pH', 'unit': '', 'range': '4.5-8.0'},
                {'name': 'Specific Gravity', 'unit': '', 'range': '1.005-1.030'},
                {'name': 'Protein', 'unit': '', 'range': 'Negative'},
                {'name': 'Glucose', 'unit': '', 'range': 'Negative'},
                {'name': 'Ketones', 'unit': '', 'range': 'Negative'},
                {'name': 'Blood', 'unit': '', 'range': 'Negative'},
                {'name': 'WBC', 'unit': '/HPF', 'range': '0-5'},
                {'name': 'RBC', 'unit': '/HPF', 'range': '0-2'},
            ]
        },
        {
            'name': 'Urine Culture',
            'code': 'UCULTURE',
            'category': 'microbiology',
            'description': 'Bacterial culture of urine',
            'turnaround_time': 72,
            'parameters': [
                {'name': 'Organism', 'unit': '', 'range': 'No Growth'},
                {'name': 'Colony Count', 'unit': 'CFU/mL', 'range': '<10,000'},
            ]
        },
        {
            'name': 'Blood Culture',
            'code': 'BCULTURE',
            'category': 'microbiology',
            'description': 'Blood bacterial culture',
            'turnaround_time': 120,
            'parameters': [
                {'name': 'Organism', 'unit': '', 'range': 'No Growth'},
            ]
        },
        {
            'name': 'Stool Culture',
            'code': 'SCULTURE',
            'category': 'microbiology',
            'description': 'Stool bacterial culture',
            'turnaround_time': 96,
            'parameters': [
                {'name': 'Pathogens', 'unit': '', 'range': 'None Detected'},
            ]
        },
        
        # Immunology Tests
        {
            'name': 'HIV Test',
            'code': 'HIV',
            'category': 'immunology',
            'description': 'HIV antibody test',
            'turnaround_time': 24,
            'parameters': [
                {'name': 'HIV 1/2', 'unit': '', 'range': 'Non-Reactive'},
            ]
        },
        {
            'name': 'Hepatitis Panel',
            'code': 'HEP',
            'category': 'immunology',
            'description': 'Hepatitis screening',
            'turnaround_time': 48,
            'parameters': [
                {'name': 'HBsAg', 'unit': '', 'range': 'Negative'},
                {'name': 'Anti-HCV', 'unit': '', 'range': 'Negative'},
                {'name': 'Anti-HBs', 'unit': '', 'range': 'Negative'},
            ]
        },
        {
            'name': 'CRP',
            'code': 'CRP',
            'category': 'immunology',
            'description': 'C-Reactive Protein',
            'turnaround_time': 12,
            'parameters': [
                {'name': 'CRP', 'unit': 'mg/L', 'range': '<10'},
            ]
        },
        
        # Molecular Tests
        {
            'name': 'COVID-19 PCR',
            'code': 'COVID',
            'category': 'molecular',
            'description': 'SARS-CoV-2 PCR test',
            'turnaround_time': 24,
            'parameters': [
                {'name': 'Result', 'unit': '', 'range': 'Negative'},
            ]
        },
        
        # Pathology Tests
        {
            'name': 'Tissue Biopsy',
            'code': 'BIOPSY',
            'category': 'pathology',
            'description': 'Histopathology examination',
            'turnaround_time': 120,
            'parameters': [
                {'name': 'Diagnosis', 'unit': '', 'range': 'Benign'},
            ]
        },
    ]
    
    for test_data in tests_data:
        parameters = test_data.pop('parameters')
        test, created = Test.objects.get_or_create(
            code=test_data['code'],
            defaults=test_data
        )
        if created:
            print(f"  ✓ Created test: {test.code} - {test.name}")
            for i, param_data in enumerate(parameters):
                TestParameter.objects.create(
                    test=test,
                    name=param_data['name'],
                    unit=param_data['unit'],
                    reference_range_text=param_data['range'],
                    order=i
                )


def create_samples():
    """Create sample records."""
    print("\nCreating samples...")
    
    technicians = User.objects.filter(role__name='technician')
    if not technicians.exists():
        print("  ⚠ No technicians found, skipping sample creation")
        return
    
    today = datetime.now().date()
    
    # Patient names pool
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'James', 'Mary',
                   'William', 'Patricia', 'Richard', 'Jennifer', 'Charles', 'Linda', 'Joseph', 'Barbara',
                   'Thomas', 'Elizabeth', 'Christopher', 'Susan', 'Daniel', 'Jessica', 'Matthew', 'Karen',
                   'Anthony', 'Nancy', 'Mark', 'Betty', 'Donald', 'Helen', 'Steven', 'Sandra', 'Paul',
                   'Ashley', 'Andrew', 'Donna', 'Joshua', 'Carol', 'Kenneth', 'Ruth', 'Kevin', 'Sharon']
    
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez',
                  'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor',
                  'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
                  'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott']
    
    sample_types = ['blood', 'urine', 'blood', 'blood', 'urine', 'tissue', 'blood']
    statuses = ['registered', 'in_progress', 'completed', 'registered', 'in_progress']
    priorities = ['normal', 'normal', 'normal', 'high', 'urgent', 'normal']
    
    samples_created = 0
    
    # Create 100 samples
    for i in range(1, 101):
        import random
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        age = random.randint(18, 85)
        gender = random.choice(['M', 'F'])
        sample_type = random.choice(sample_types)
        status = random.choice(statuses)
        priority = random.choice(priorities)
        days_ago = random.randint(0, 30)
        
        sample_id = f'S2025-{i:04d}'
        source = f'{first_name} {last_name} ({age}/{gender})'
        
        sample, created = Sample.objects.get_or_create(
            sample_id=sample_id,
            defaults={
                'sample_type': sample_type,
                'source': source,
                'received_date': today - timedelta(days=days_ago),
                'status': status,
                'priority': priority,
                'registered_by': User.objects.first(),
                'assigned_technician': technicians[i % len(technicians)],
                'notes': f'Sample received from {source}' if i % 5 == 0 else ''
            }
        )
        if created:
            samples_created += 1
    
    print(f"  ✓ Created {samples_created} samples")


def create_test_assignments():
    """Create test assignments for samples."""
    print("\nCreating test assignments...")
    
    samples = Sample.objects.all()
    tests = Test.objects.all()
    technicians = list(User.objects.filter(role__name='technician'))
    
    if not samples.exists() or not tests.exists():
        print("  ⚠ No samples or tests found, skipping")
        return
    
    import random
    
    # Define common test combinations
    test_combinations = {
        'blood': [
            ['CBC', 'DIFF'],
            ['CBC', 'LFT', 'RFT'],
            ['CBC', 'LIPID', 'GLU'],
            ['LFT', 'RFT'],
            ['LIPID', 'GLU', 'HBA1C'],
            ['TFT', 'ELEC'],
            ['HIV', 'HEP'],
            ['CBC'],
            ['LFT'],
            ['RFT'],
            ['CARDIAC'],
        ],
        'urine': [
            ['UA'],
            ['UA', 'UCULTURE'],
        ],
        'tissue': [
            ['BIOPSY'],
        ]
    }
    
    statuses = ['assigned', 'in_progress', 'completed', 'in_progress', 'completed']
    assignments_created = 0
    
    for sample in samples:
        # Get appropriate test combinations for sample type
        sample_type = sample.sample_type if sample.sample_type in test_combinations else 'blood'
        possible_combinations = test_combinations[sample_type]
        
        # Pick a random combination
        test_codes = random.choice(possible_combinations)
        
        for test_code in test_codes:
            try:
                test = Test.objects.get(code=test_code)
                status = random.choice(statuses)
                
                assignment, created = TestAssignment.objects.get_or_create(
                    sample=sample,
                    test=test,
                    defaults={
                        'status': status,
                        'assigned_to': random.choice(technicians),
                        'assigned_by': User.objects.first(),
                    }
                )
                if created:
                    assignments_created += 1
                    
                    # If completed, create a result entry
                    if status == 'completed' and random.random() > 0.3:
                        create_result_for_assignment(assignment)
                        
            except Test.DoesNotExist:
                continue
    
    print(f"  ✓ Created {assignments_created} test assignments")


def create_result_for_assignment(assignment):
    """Create a result for a completed test assignment."""
    from results.models import TestResult
    from datetime import datetime
    from decimal import Decimal
    
    # Get test parameters
    test = assignment.test
    
    # Randomly choose status: 60% approved, 30% pending_review, 10% draft
    import random
    rand_val = random.random()
    if rand_val < 0.6:
        status = 'approved'
    elif rand_val < 0.9:
        status = 'pending_review'
    else:
        status = 'draft'
    
    # Create a result if it doesn't exist
    result, created = TestResult.objects.get_or_create(
        test_assignment=assignment,
        defaults={
            'entered_by': assignment.assigned_to,
            'status': status,
            'comments': 'Results within normal limits' if hash(str(assignment.id)) % 10 > 1 else 'Some abnormal values detected',
        }
    )
    
    if created:
        # Create parameter results
        from results.models import ParameterResult
        
        for param in test.parameters.all():
            # Generate a realistic value within or slightly outside range
            if param.reference_range_min and param.reference_range_max:
                min_val = float(param.reference_range_min)
                max_val = float(param.reference_range_max)
                range_width = max_val - min_val
                
                # 80% within range, 20% slightly out of range
                if random.random() < 0.8:
                    value = min_val + (random.random() * range_width)
                else:
                    # Slightly outside range
                    if random.random() < 0.5:
                        value = min_val - (random.random() * range_width * 0.2)
                    else:
                        value = max_val + (random.random() * range_width * 0.2)
                
                value = round(value, 2)
            else:
                # If no range, use a random reasonable value
                value = round(random.random() * 100, 2)
            
            param_result = ParameterResult.objects.create(
                test_result=result,
                parameter=param,
                value_numeric=Decimal(str(value))
            )
            # Check if abnormal
            param_result.check_abnormal()
            param_result.save()



def create_inventory():
    """Create inventory items."""
    print("\nCreating inventory items...")
    
    today = datetime.now().date()
    
    # Reagents - expanded to 40 items
    reagents_data = [
        # Hematology reagents
        ('HEM-001', 'Hemoglobin Reagent', 'BioLab Inc', 500, 'mL', 100, 180),
        ('HEM-002', 'WBC Differential Stain', 'Sysmex', 300, 'mL', 60, 150),
        ('HEM-003', 'Reticulocyte Reagent', 'Beckman Coulter', 250, 'mL', 50, 120),
        ('HEM-004', 'EDTA Anticoagulant', 'BD', 1000, 'mL', 200, 200),
        
        # Biochemistry reagents
        ('GLU-501', 'Glucose Test Reagent', 'Roche', 800, 'mL', 150, 90),
        ('LFT-101', 'ALT Reagent', 'Abbott', 600, 'mL', 120, 90),
        ('LFT-102', 'AST Reagent', 'Abbott', 600, 'mL', 120, 90),
        ('LFT-103', 'Bilirubin Reagent', 'Siemens', 400, 'mL', 80, 90),
        ('LFT-104', 'Albumin Reagent', 'Roche', 500, 'mL', 100, 90),
        ('RFT-201', 'Creatinine Reagent', 'Roche', 700, 'mL', 140, 90),
        ('RFT-202', 'Urea Reagent', 'Abbott', 650, 'mL', 130, 90),
        ('LIP-301', 'Cholesterol Reagent', 'Siemens', 550, 'mL', 110, 90),
        ('LIP-302', 'Triglyceride Reagent', 'Roche', 500, 'mL', 100, 90),
        ('LIP-303', 'HDL Reagent', 'Abbott', 450, 'mL', 90, 90),
        ('LIP-304', 'LDL Reagent', 'Siemens', 400, 'mL', 80, 90),
        ('ELEC-401', 'Sodium ISE Reagent', 'Roche', 600, 'mL', 120, 120),
        ('ELEC-402', 'Potassium ISE Reagent', 'Abbott', 580, 'mL', 115, 120),
        ('ELEC-403', 'Chloride ISE Reagent', 'Siemens', 550, 'mL', 110, 120),
        
        # Microbiology reagents
        ('CULT-601', 'Blood Agar Plates', 'BD', 100, 'plates', 20, 60),
        ('CULT-602', 'MacConkey Agar', 'Oxoid', 80, 'plates', 15, 60),
        ('CULT-603', 'Mueller Hinton Agar', 'BD', 70, 'plates', 15, 60),
        ('CULT-604', 'Sabouraud Agar', 'Oxoid', 50, 'plates', 10, 60),
        ('CULT-605', 'Nutrient Broth', 'BD', 500, 'mL', 100, 90),
        ('STAIN-701', 'Gram Stain Kit', 'Merck', 50, 'kits', 10, 120),
        ('STAIN-702', 'Acid-Fast Stain', 'Sigma', 30, 'kits', 5, 120),
        ('ANTI-801', 'Antibiotic Disc Set', 'Oxoid', 200, 'discs', 40, 180),
        
        # Immunology reagents
        ('ELISA-901', 'HIV ELISA Kit', 'Bio-Rad', 96, 'tests', 20, 30),
        ('ELISA-902', 'HBsAg ELISA Kit', 'Abbott', 96, 'tests', 20, 30),
        ('ELISA-903', 'Anti-HCV Kit', 'Bio-Rad', 96, 'tests', 20, 30),
        ('IMM-910', 'CRP Reagent', 'Siemens', 400, 'mL', 80, 90),
        
        # Molecular biology
        ('PCR-1001', 'COVID-19 RT-PCR Kit', 'Thermo Fisher', 100, 'tests', 20, 30),
        ('PCR-1002', 'RNA Extraction Kit', 'Qiagen', 50, 'preps', 10, 60),
        ('PCR-1003', 'DNA Extraction Kit', 'Qiagen', 50, 'preps', 10, 60),
        
        # General supplies
        ('BUF-704', 'Buffer Solution pH 7.4', 'ChemCorp', 1000, 'mL', 200, 365),
        ('URI-100', 'Urine Test Strips', 'LabTest Ltd', 200, 'strips', 50, 60),
        ('CAL-1101', 'Multi-Calibrator', 'Roche', 200, 'mL', 40, 90),
        ('QC-1201', 'Quality Control Serum', 'Bio-Rad', 150, 'mL', 30, 60),
        ('DH2O-1301', 'Distilled Water', 'In-house', 5000, 'mL', 1000, 365),
        ('ETOH-1401', 'Ethanol 70%', 'VWR', 2000, 'mL', 400, 180),
        ('FORM-1501', 'Formaldehyde 10%', 'Sigma', 500, 'mL', 100, 180),
    ]
    
    reagents_created = 0
    for cat_num, name, manufacturer, qty, unit, min_qty, exp_days in reagents_data:
        reagent, created = Reagent.objects.get_or_create(
            catalog_number=cat_num,
            defaults={
                'name': name,
                'manufacturer': manufacturer,
                'quantity': qty,
                'unit': unit,
                'minimum_quantity': min_qty,
                'expiry_date': today + timedelta(days=exp_days),
            }
        )
        if created:
            reagents_created += 1
    
    print(f"  ✓ Created {reagents_created} reagents")
    
    # Stock Items - expanded to 35 items
    stock_data = [
        # Consumables
        ('BCT-EDTA-001', 'Blood Collection Tubes (EDTA)', 'Consumables', 500, 'tubes', 100),
        ('BCT-LH-002', 'Blood Collection Tubes (Li-Hep)', 'Consumables', 400, 'tubes', 80),
        ('BCT-SST-003', 'Blood Collection Tubes (SST)', 'Consumables', 450, 'tubes', 90),
        ('PT-10-001', 'Pipette Tips 10μL', 'Consumables', 5000, 'pieces', 1000),
        ('PT-200-002', 'Pipette Tips 200μL', 'Consumables', 4500, 'pieces', 900),
        ('PT-1000-001', 'Pipette Tips 1000μL', 'Consumables', 2000, 'pieces', 500),
        ('MCT-15-001', 'Microcentrifuge Tubes 1.5mL', 'Consumables', 3000, 'pieces', 600),
        ('TT-15-001', 'Test Tubes 15mL', 'Consumables', 2500, 'pieces', 500),
        ('TT-50-001', 'Test Tubes 50mL', 'Consumables', 2000, 'pieces', 400),
        ('SL-001', 'Glass Slides', 'Consumables', 1000, 'pieces', 200),
        ('CS-001', 'Cover Slips', 'Consumables', 1500, 'pieces', 300),
        ('PD-90-001', 'Petri Dishes 90mm', 'Consumables', 800, 'pieces', 160),
        ('SW-001', 'Sterile Swabs', 'Consumables', 1200, 'pieces', 240),
        ('SY-5-001', 'Syringes 5mL', 'Consumables', 600, 'pieces', 120),
        ('ND-21-001', 'Needles 21G', 'Consumables', 800, 'pieces', 160),
        ('AS-001', 'Alcohol Swabs', 'Consumables', 2000, 'pieces', 400),
        
        # PPE
        ('GLV-NIT-S', 'Gloves (Nitrile, Small)', 'PPE', 40, 'boxes', 10),
        ('GLV-NIT-M', 'Gloves (Nitrile, Medium)', 'PPE', 60, 'boxes', 15),
        ('GLV-NIT-L', 'Gloves (Nitrile, Large)', 'PPE', 70, 'boxes', 18),
        ('LC-M-001', 'Lab Coats Medium', 'PPE', 30, 'pieces', 8),
        ('LC-L-001', 'Lab Coats Large', 'PPE', 35, 'pieces', 10),
        ('FM-001', 'Face Masks', 'PPE', 1000, 'pieces', 200),
        ('SG-001', 'Safety Goggles', 'PPE', 40, 'pieces', 10),
        
        # Equipment/Supplies
        ('SR-50-001', 'Sample Racks', 'Equipment', 25, 'pieces', 10),
        ('PCK-001', 'Pipette Calibration Kit', 'Equipment', 5, 'kits', 2),
        ('CR-001', 'Centrifuge Rotor', 'Equipment', 4, 'pieces', 1),
        ('IS-001', 'Incubator Shelves', 'Equipment', 10, 'pieces', 3),
        ('MB-001', 'Microscope Bulbs', 'Equipment', 20, 'pieces', 5),
        ('PHE-001', 'pH Electrode', 'Equipment', 5, 'pieces', 2),
        
        # Cleaning/Waste
        ('DET-001', 'Detergent Solution', 'Cleaning', 500, 'mL', 100),
        ('DIS-001', 'Disinfectant Spray', 'Cleaning', 300, 'mL', 60),
        ('WB-BIO-001', 'Waste Bags Biohazard', 'Cleaning', 200, 'pieces', 40),
        ('SC-001', 'Sharps Container', 'Cleaning', 15, 'pieces', 5),
        
        # Office/Documentation
        ('LPP-001', 'Label Printer Paper', 'Office', 50, 'rolls', 10),
        ('SL-LABEL-001', 'Sample Labels', 'Office', 1000, 'pieces', 200),
    ]
    
    stock_created = 0
    for item_code, name, category, qty, unit, min_qty in stock_data:
        item, created = StockItem.objects.get_or_create(
            item_code=item_code,
            defaults={
                'name': name,
                'category': category,
                'quantity': qty,
                'unit': unit,
                'minimum_quantity': min_qty,
            }
        )
        if created:
            stock_created += 1
    
    print(f"  ✓ Created {stock_created} stock items")



def create_instruments():
    """Create instrument records."""
    print("\nCreating instruments...")
    
    today = datetime.now().date()
    
    # Expanded instruments data - 15 instruments
    instruments_data = [
        # Hematology instruments
        ('HC5000-2024-001', 'Hematology Analyzer', 'HemCount 5000', 'Sysmex', 'operational', 'Hematology Lab', 365, 90, 30),
        ('HC3000-2023-012', 'Automated Cell Counter', 'HemCount 3000', 'Beckman Coulter', 'operational', 'Hematology Lab', 450, 90, 45),
        ('ESR-2024-003', 'ESR Analyzer', 'ESR-Auto', 'Greiner Bio-One', 'operational', 'Hematology Lab', 200, 180, 90),
        
        # Biochemistry instruments
        ('CP3000-2023-042', 'Chemistry Analyzer', 'ChemPro 3000', 'Roche Diagnostics', 'operational', 'Chemistry Lab', 500, 90, 60),
        ('BA-2024-007', 'Biochemistry Analyzer', 'Cobas c111', 'Roche Diagnostics', 'operational', 'Chemistry Lab', 300, 90, 50),
        ('ELEC-2023-018', 'Electrolyte Analyzer', 'EasyLyte Plus', 'Medica', 'calibration', 'Chemistry Lab', 400, 90, 5),
        
        # General lab equipment
        ('SM2000-2024-015', 'Centrifuge High Speed', 'SpinMax 2000', 'Eppendorf', 'operational', 'Sample Prep', 200, 180, 120),
        ('CENT-2023-009', 'Microcentrifuge', 'MiniSpin Plus', 'Eppendorf', 'operational', 'Sample Prep', 350, 180, 95),
        ('INC-2024-011', 'CO2 Incubator', 'HERAcell 150i', 'Thermo Fisher', 'operational', 'Microbiology Lab', 250, 180, 100),
        ('WB-2023-025', 'Water Bath', 'Precision 2875', 'Thermo Fisher', 'operational', 'General Lab', 400, 180, 110),
        
        # Microbiology instruments
        ('MVP-2024-008', 'Microscope Digital', 'MicroView Pro', 'Olympus', 'operational', 'Microbiology Lab', 100, 180, 85),
        ('MICRO-2023-014', 'Microscope Binocular', 'CX23', 'Olympus', 'operational', 'Microbiology Lab', 500, 180, 120),
        ('AUTO-2024-002', 'Automated Incubator', 'BacT/Alert 3D', 'BioMérieux', 'operational', 'Microbiology Lab', 180, 90, 40),
        
        # Molecular biology instruments
        ('PCR-2024-001', 'Real-Time PCR System', 'QuantStudio 5', 'Thermo Fisher', 'operational', 'Molecular Lab', 150, 90, 55),
        ('THERMO-2023-020', 'Thermal Cycler', 'T100', 'Bio-Rad', 'maintenance', 'Molecular Lab', 280, 180, -10),
    ]
    
    instruments_created = 0
    for serial, name, model, manufacturer, status, location, days_ago, cal_freq, next_cal_days in instruments_data:
        instrument, created = Instrument.objects.get_or_create(
            serial_number=serial,
            defaults={
                'name': name,
                'model': model,
                'manufacturer': manufacturer,
                'status': status,
                'purchase_date': today - timedelta(days=days_ago),
                'calibration_frequency': cal_freq,
                'next_calibration_date': today + timedelta(days=next_cal_days),
                'location': location,
            }
        )
        if created:
            instruments_created += 1
            
            # Add 1-3 calibration records for each instrument
            import random
            num_calibrations = random.randint(1, 3)
            for i in range(num_calibrations):
                cal_days_ago = days_ago - (i * cal_freq) - random.randint(0, 15)
                if cal_days_ago > 0:
                    CalibrationRecord.objects.create(
                        instrument=instrument,
                        calibration_date=today - timedelta(days=cal_days_ago),
                        performed_by=User.objects.filter(role__name='technician').first() or User.objects.first(),
                        passed=random.random() > 0.1,
                        standards_used='ISO Standard Reference Material',
                        results='All parameters within specifications' if i == 0 else 'Routine calibration completed',
                        notes=f'Routine calibration - All parameters within acceptable ranges' if i == 0 else 'Scheduled calibration',
                        next_calibration_date=today - timedelta(days=cal_days_ago) + timedelta(days=cal_freq)
                    )
    
    print(f"  ✓ Created {instruments_created} instruments")


def main():
    """Main function to populate data."""
    print("=" * 60)
    print("LIMS Database Population Script")
    print("=" * 60)
    
    try:
        create_roles()
        create_users()
        create_tests()
        create_samples()
        create_test_assignments()
        create_inventory()
        create_instruments()
        
        print("\n" + "=" * 60)
        print("✓ Database populated successfully!")
        print("=" * 60)
        print("\nTest Users Created:")
        print("  - admin / password123 (Administrator)")
        print("  - tech1 / password123 (Lab Technician)")
        print("  - tech2 / password123 (Lab Technician)")
        print("  - manager / password123 (Lab Manager)")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
