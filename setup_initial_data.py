#!/usr/bin/env python
"""
Initial data setup script for Django LIMS
Run this after creating your superuser account.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims_project.settings')
django.setup()

from users.models import Role, User
from tests.models import Test, TestParameter


def create_roles():
    """Create default roles."""
    print("Creating roles...")
    
    roles_data = [
        {
            'name': 'admin',
            'description': 'System Administrator - Full access',
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
            'name': 'lab_manager',
            'description': 'Laboratory Manager - Manages lab operations',
            'can_register_samples': True,
            'can_assign_tests': True,
            'can_enter_results': True,
            'can_approve_results': True,
            'can_manage_inventory': True,
            'can_manage_instruments': True,
            'can_view_reports': True,
            'can_manage_users': False,
        },
        {
            'name': 'technician',
            'description': 'Laboratory Technician - Performs tests',
            'can_register_samples': True,
            'can_assign_tests': True,
            'can_enter_results': True,
            'can_approve_results': False,
            'can_manage_inventory': False,
            'can_manage_instruments': False,
            'can_view_reports': True,
            'can_manage_users': False,
        },
        {
            'name': 'reviewer',
            'description': 'Results Reviewer - Reviews and approves results',
            'can_register_samples': False,
            'can_assign_tests': False,
            'can_enter_results': False,
            'can_approve_results': True,
            'can_manage_inventory': False,
            'can_manage_instruments': False,
            'can_view_reports': True,
            'can_manage_users': False,
        },
        {
            'name': 'viewer',
            'description': 'Viewer - Read-only access',
            'can_register_samples': False,
            'can_assign_tests': False,
            'can_enter_results': False,
            'can_approve_results': False,
            'can_manage_inventory': False,
            'can_manage_instruments': False,
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
            print(f"✓ Created role: {role.get_name_display()}")
        else:
            print(f"  Role already exists: {role.get_name_display()}")


def create_sample_tests():
    """Create sample test types."""
    print("\nCreating sample test types...")
    
    tests_data = [
        {
            'name': 'Complete Blood Count (CBC)',
            'code': 'CBC',
            'category': 'hematology',
            'description': 'Comprehensive blood analysis',
            'turnaround_time': 24,
            'parameters': [
                {'name': 'White Blood Cells', 'unit': '10^3/μL', 'min': 4.0, 'max': 11.0},
                {'name': 'Red Blood Cells', 'unit': '10^6/μL', 'min': 4.5, 'max': 5.5},
                {'name': 'Hemoglobin', 'unit': 'g/dL', 'min': 13.5, 'max': 17.5},
                {'name': 'Hematocrit', 'unit': '%', 'min': 38.0, 'max': 50.0},
                {'name': 'Platelets', 'unit': '10^3/μL', 'min': 150.0, 'max': 400.0},
            ]
        },
        {
            'name': 'Basic Metabolic Panel',
            'code': 'BMP',
            'category': 'biochemistry',
            'description': 'Basic blood chemistry panel',
            'turnaround_time': 24,
            'parameters': [
                {'name': 'Glucose', 'unit': 'mg/dL', 'min': 70.0, 'max': 100.0},
                {'name': 'Calcium', 'unit': 'mg/dL', 'min': 8.5, 'max': 10.5},
                {'name': 'Sodium', 'unit': 'mEq/L', 'min': 136.0, 'max': 145.0},
                {'name': 'Potassium', 'unit': 'mEq/L', 'min': 3.5, 'max': 5.0},
                {'name': 'Chloride', 'unit': 'mEq/L', 'min': 98.0, 'max': 107.0},
            ]
        },
        {
            'name': 'Urinalysis',
            'code': 'UA',
            'category': 'biochemistry',
            'description': 'Complete urine analysis',
            'turnaround_time': 12,
            'parameters': [
                {'name': 'Color', 'unit': '', 'min': None, 'max': None},
                {'name': 'Clarity', 'unit': '', 'min': None, 'max': None},
                {'name': 'pH', 'unit': '', 'min': 4.5, 'max': 8.0},
                {'name': 'Specific Gravity', 'unit': '', 'min': 1.005, 'max': 1.030},
                {'name': 'Protein', 'unit': 'mg/dL', 'min': 0.0, 'max': 10.0},
            ]
        },
        {
            'name': 'COVID-19 PCR Test',
            'code': 'COVID-PCR',
            'category': 'molecular',
            'description': 'RT-PCR test for SARS-CoV-2',
            'turnaround_time': 48,
            'parameters': [
                {'name': 'Result', 'unit': '', 'min': None, 'max': None},
                {'name': 'CT Value', 'unit': '', 'min': None, 'max': None},
            ]
        },
        {
            'name': 'Water Quality Test',
            'code': 'H2O-QUAL',
            'category': 'other',
            'description': 'Environmental water quality analysis',
            'turnaround_time': 72,
            'parameters': [
                {'name': 'pH', 'unit': '', 'min': 6.5, 'max': 8.5},
                {'name': 'Turbidity', 'unit': 'NTU', 'min': 0.0, 'max': 5.0},
                {'name': 'Total Dissolved Solids', 'unit': 'mg/L', 'min': 0.0, 'max': 500.0},
                {'name': 'Total Coliform', 'unit': 'CFU/100mL', 'min': 0.0, 'max': 0.0},
            ]
        },
    ]
    
    for test_data in tests_data:
        parameters_data = test_data.pop('parameters')
        test, created = Test.objects.get_or_create(
            code=test_data['code'],
            defaults=test_data
        )
        
        if created:
            print(f"✓ Created test: {test.name}")
            
            # Create parameters
            for i, param_data in enumerate(parameters_data):
                TestParameter.objects.create(
                    test=test,
                    name=param_data['name'],
                    unit=param_data['unit'],
                    reference_range_min=param_data['min'],
                    reference_range_max=param_data['max'],
                    order=i
                )
            print(f"  Added {len(parameters_data)} parameters")
        else:
            print(f"  Test already exists: {test.name}")


def main():
    """Main setup function."""
    print("=" * 60)
    print("Django LIMS - Initial Data Setup")
    print("=" * 60)
    print()
    
    try:
        # Create roles
        create_roles()
        
        # Create sample tests
        create_sample_tests()
        
        print()
        print("=" * 60)
        print("✓ Setup completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Create users and assign roles via /users/list/")
        print("2. Add more test types as needed")
        print("3. Register instruments and inventory items")
        print("4. Start registering samples!")
        print()
        
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
