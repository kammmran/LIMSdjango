"""
Populate synthetic data for the Lab Management module
Run this script with: python manage.py shell < populate_labs_data.py
Or: python populate_labs_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims_project.settings')
django.setup()

from labs.models import Lab, Person, ResearchProject, Task
from django.contrib.auth import get_user_model

User = get_user_model()

def create_synthetic_data():
    print("🧪 Starting Lab Management data population...")
    
    # Create or get admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Created admin user: {admin_user.username}")
    else:
        print(f"ℹ️  Using existing admin user: {admin_user.username}")
    
    # Clear existing data
    print("\n🗑️  Clearing existing lab data...")
    Task.objects.all().delete()
    ResearchProject.objects.all().delete()
    Person.objects.all().delete()
    Lab.objects.all().delete()
    
    # Create Labs
    print("\n🏢 Creating Labs...")
    labs_data = [
        {
            'name': 'Molecular Biology Lab',
            'code': 'MBL-001',
            'description': 'Advanced molecular biology research focusing on gene expression and protein analysis',
            'location': 'Building A, Floor 3, Room 301',
            'research_focus': 'Gene expression, protein analysis, molecular diagnostics',
            'is_active': True
        },
        {
            'name': 'Clinical Chemistry Lab',
            'code': 'CCL-002',
            'description': 'Clinical testing and diagnostic chemistry services',
            'location': 'Building B, Floor 2, Room 205',
            'research_focus': 'Clinical diagnostics, biomarker discovery, metabolomics',
            'is_active': True
        },
        {
            'name': 'Microbiology Lab',
            'code': 'MCB-003',
            'description': 'Bacterial and viral research, pathogen identification',
            'location': 'Building A, Floor 4, Room 402',
            'research_focus': 'Microbial pathogenesis, antibiotic resistance, virology',
            'is_active': True
        },
        {
            'name': 'Genetics & Genomics Lab',
            'code': 'GGL-004',
            'description': 'DNA sequencing, genetic analysis, and genomic research',
            'location': 'Building C, Floor 1, Room 105',
            'research_focus': 'Genomics, gene editing, personalized medicine',
            'is_active': True
        },
        {
            'name': 'Pathology Lab',
            'code': 'PTH-005',
            'description': 'Tissue analysis, histopathology, and diagnostic services',
            'location': 'Building B, Floor 3, Room 310',
            'research_focus': 'Histopathology, tissue regeneration, cancer biology',
            'is_active': True
        }
    ]
    
    labs = []
    for lab_data in labs_data:
        lab = Lab.objects.create(**lab_data)
        labs.append(lab)
        print(f"  ✓ Created: {lab.name} ({lab.code})")
    
    # Create People
    print("\n👥 Creating People...")
    people_data = [
        {
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@research.edu',
            'phone': '+1-555-1001',
            'role': 'lab_manager',
            'position': 'Principal Investigator - Molecular Biology',
            'lab': labs[0],  # Molecular Biology Lab
            'user': admin_user,
            'is_active': True
        },
        {
            'first_name': 'Michael',
            'last_name': 'Chen',
            'email': 'michael.chen@research.edu',
            'phone': '+1-555-1002',
            'role': 'researcher',
            'position': 'Research Scientist',
            'lab': labs[0],
            'is_active': True
        },
        {
            'first_name': 'Emily',
            'last_name': 'Rodriguez',
            'email': 'emily.rodriguez@research.edu',
            'phone': '+1-555-1003',
            'role': 'assistant',
            'position': 'Lab Technician',
            'lab': labs[1],  # Clinical Chemistry Lab
            'is_active': True
        },
        {
            'first_name': 'David',
            'last_name': 'Patel',
            'email': 'david.patel@research.edu',
            'phone': '+1-555-1004',
            'role': 'lab_manager',
            'position': 'Principal Investigator - Microbiology',
            'lab': labs[2],  # Microbiology Lab
            'is_active': True
        },
        {
            'first_name': 'Jessica',
            'last_name': 'Williams',
            'email': 'jessica.williams@research.edu',
            'phone': '+1-555-1005',
            'role': 'researcher',
            'position': 'Research Associate',
            'lab': labs[2],
            'is_active': True
        },
        {
            'first_name': 'Robert',
            'last_name': 'Anderson',
            'email': 'robert.anderson@research.edu',
            'phone': '+1-555-1006',
            'role': 'researcher',
            'position': 'Senior Scientist',
            'lab': labs[3],  # Genetics & Genomics Lab
            'is_active': True
        },
        {
            'first_name': 'Lisa',
            'last_name': 'Martinez',
            'email': 'lisa.martinez@research.edu',
            'phone': '+1-555-1007',
            'role': 'lab_manager',
            'position': 'Lab Manager - Pathology',
            'lab': labs[4],  # Pathology Lab
            'is_active': True
        },
        {
            'first_name': 'James',
            'last_name': 'Thompson',
            'email': 'james.thompson@research.edu',
            'phone': '+1-555-1008',
            'role': 'assistant',
            'position': 'Research Technician',
            'lab': labs[3],
            'is_active': True
        }
    ]
    
    people = []
    for person_data in people_data:
        person = Person.objects.create(**person_data)
        people.append(person)
        print(f"  ✓ Created: {person.first_name} {person.last_name} - {person.position}")
    
    # Set lab heads
    labs[0].head_of_lab = people[0]  # Sarah Johnson
    labs[0].save()
    labs[1].head_of_lab = people[2]  # Emily Rodriguez
    labs[1].save()
    labs[2].head_of_lab = people[3]  # David Patel
    labs[2].save()
    labs[3].head_of_lab = people[5]  # Robert Anderson
    labs[3].save()
    labs[4].head_of_lab = people[6]  # Lisa Martinez
    labs[4].save()
    print("\n  ✓ Assigned lab heads")
    
    # Create Research Projects
    print("\n📊 Creating Research Projects...")
    projects_data = [
        {
            'title': 'COVID-19 Variant Analysis',
            'summary': 'Comprehensive study of SARS-CoV-2 variants and their impact on transmissibility. Project code: PRJ-2024-001',
            'lab': labs[2],  # Microbiology Lab
            'principal_investigator': people[3],  # David Patel
            'start_date': datetime.now().date() - timedelta(days=90),
            'end_date': datetime.now().date() + timedelta(days=275),
            'status': 'active',
            'budget': Decimal('250000.00'),
            'funding_source': 'NIH Grant R01-AI-2024-001',
            'priority': 'high'
        },
        {
            'title': 'Protein Folding Mechanisms',
            'summary': 'Investigation of protein misfolding in neurodegenerative diseases. Project code: PRJ-2024-002',
            'lab': labs[0],  # Molecular Biology Lab
            'principal_investigator': people[0],  # Sarah Johnson
            'start_date': datetime.now().date() - timedelta(days=180),
            'end_date': datetime.now().date() + timedelta(days=545),
            'status': 'active',
            'budget': Decimal('500000.00'),
            'funding_source': 'NSF Grant DBI-2024-002',
            'priority': 'high'
        },
        {
            'title': 'Biomarker Discovery for Early Cancer Detection',
            'summary': 'Identifying novel biomarkers for early-stage cancer detection in blood samples. Project code: PRJ-2024-003',
            'lab': labs[1],  # Clinical Chemistry Lab
            'principal_investigator': people[2],  # Emily Rodriguez
            'start_date': datetime.now().date() - timedelta(days=60),
            'end_date': datetime.now().date() + timedelta(days=305),
            'status': 'active',
            'budget': Decimal('350000.00'),
            'funding_source': 'Cancer Research Foundation',
            'priority': 'high'
        },
        {
            'title': 'CRISPR Gene Editing Optimization',
            'summary': 'Optimizing CRISPR-Cas9 techniques for therapeutic applications. Project code: PRJ-2024-004',
            'lab': labs[3],  # Genetics & Genomics Lab
            'principal_investigator': people[5],  # Robert Anderson
            'start_date': datetime.now().date() - timedelta(days=120),
            'end_date': datetime.now().date() + timedelta(days=245),
            'status': 'active',
            'budget': Decimal('450000.00'),
            'funding_source': 'Gates Foundation',
            'priority': 'high'
        },
        {
            'title': 'Antibiotic Resistance Mechanisms',
            'summary': 'Study of bacterial resistance mechanisms and development of new antimicrobials. Project code: PRJ-2024-005',
            'lab': labs[2],  # Microbiology Lab
            'principal_investigator': people[3],  # David Patel
            'start_date': datetime.now().date() - timedelta(days=200),
            'end_date': datetime.now().date() + timedelta(days=165),
            'status': 'active',
            'budget': Decimal('300000.00'),
            'funding_source': 'WHO Research Grant',
            'priority': 'high'
        },
        {
            'title': 'Tissue Regeneration Study',
            'summary': 'Investigating stem cell-based tissue regeneration approaches. Project code: PRJ-2024-006',
            'lab': labs[4],  # Pathology Lab
            'principal_investigator': people[6],  # Lisa Martinez
            'start_date': datetime.now().date() - timedelta(days=30),
            'end_date': datetime.now().date() + timedelta(days=335),
            'status': 'active',
            'budget': Decimal('400000.00'),
            'funding_source': 'NIH Grant R01-GM-2024-003',
            'priority': 'medium'
        }
    ]
    
    projects = []
    for project_data in projects_data:
        project = ResearchProject.objects.create(**project_data)
        # Add team members
        if project.lab == labs[0]:  # Molecular Biology
            project.team_members.add(people[0], people[1])
        elif project.lab == labs[1]:  # Clinical Chemistry
            project.team_members.add(people[2])
        elif project.lab == labs[2]:  # Microbiology
            project.team_members.add(people[3], people[4])
        elif project.lab == labs[3]:  # Genetics
            project.team_members.add(people[5], people[7])
        elif project.lab == labs[4]:  # Pathology
            project.team_members.add(people[6])
        
        projects.append(project)
        print(f"  ✓ Created: {project.title}")
    
    # Create Tasks
    print("\n📋 Creating Tasks...")
    tasks_data = [
        # COVID-19 Project Tasks
        {
            'title': 'Sample Collection - Wave 1',
            'project': projects[0],
            'assigned_to': people[4],
            'description': 'Collect 200 patient samples for variant sequencing',
            'status': 'done',
            'priority': 'high',
            'deadline': datetime.now().date() - timedelta(days=30),
        },
        {
            'title': 'RNA Extraction and Purification',
            'project': projects[0],
            'assigned_to': people[4],
            'description': 'Extract and purify RNA from collected samples',
            'status': 'in_progress',
            'priority': 'high',
            'deadline': datetime.now().date() + timedelta(days=7),
        },
        {
            'title': 'Variant Sequencing',
            'project': projects[0],
            'assigned_to': people[3],
            'description': 'Perform whole genome sequencing on prepared samples',
            'status': 'todo',
            'priority': 'urgent',
            'deadline': datetime.now().date() + timedelta(days=21),
        },
        
        # Protein Folding Project Tasks
        {
            'title': 'Literature Review',
            'project': projects[1],
            'assigned_to': people[1],
            'description': 'Comprehensive review of recent protein folding research',
            'status': 'done',
            'priority': 'medium',
            'deadline': datetime.now().date() - timedelta(days=60),
        },
        {
            'title': 'Protein Expression Protocol',
            'project': projects[1],
            'assigned_to': people[0],
            'description': 'Develop optimized protein expression protocol',
            'status': 'in_progress',
            'priority': 'high',
            'deadline': datetime.now().date() + timedelta(days=14),
        },
        {
            'title': 'Fluorescence Microscopy Setup',
            'project': projects[1],
            'assigned_to': people[1],
            'description': 'Configure microscopy equipment for protein imaging',
            'status': 'in_progress',
            'priority': 'medium',
            'deadline': datetime.now().date() + timedelta(days=5),
        },
        
        # Biomarker Discovery Tasks
        {
            'title': 'Patient Recruitment',
            'project': projects[2],
            'assigned_to': people[2],
            'description': 'Recruit 500 patients for biomarker study',
            'status': 'in_progress',
            'priority': 'urgent',
            'deadline': datetime.now().date() + timedelta(days=30),
        },
        {
            'title': 'Blood Sample Processing',
            'project': projects[2],
            'assigned_to': people[2],
            'description': 'Process and catalog blood samples',
            'status': 'todo',
            'priority': 'high',
            'deadline': datetime.now().date() + timedelta(days=45),
        },
        
        # CRISPR Project Tasks
        {
            'title': 'Guide RNA Design',
            'project': projects[3],
            'assigned_to': people[7],
            'description': 'Design and validate guide RNAs for target genes',
            'status': 'done',
            'priority': 'high',
            'deadline': datetime.now().date() - timedelta(days=15),
        },
        {
            'title': 'Cell Line Preparation',
            'project': projects[3],
            'assigned_to': people[5],
            'description': 'Prepare and validate cell lines for editing',
            'status': 'in_progress',
            'priority': 'high',
            'deadline': datetime.now().date() + timedelta(days=10),
        },
        {
            'title': 'Editing Efficiency Analysis',
            'project': projects[3],
            'assigned_to': people[7],
            'description': 'Analyze editing efficiency across different conditions',
            'status': 'todo',
            'priority': 'medium',
            'deadline': datetime.now().date() + timedelta(days=25),
        },
        
        # Antibiotic Resistance Tasks
        {
            'title': 'Bacterial Strain Isolation',
            'project': projects[4],
            'assigned_to': people[4],
            'description': 'Isolate resistant bacterial strains from clinical samples',
            'status': 'done',
            'priority': 'urgent',
            'deadline': datetime.now().date() - timedelta(days=45),
        },
        {
            'title': 'Resistance Mechanism Analysis',
            'project': projects[4],
            'assigned_to': people[3],
            'description': 'Characterize molecular mechanisms of resistance',
            'status': 'in_progress',
            'priority': 'urgent',
            'deadline': datetime.now().date() + timedelta(days=20),
        },
        
        # Tissue Regeneration Tasks
        {
            'title': 'Ethics Approval Application',
            'project': projects[5],
            'assigned_to': people[6],
            'description': 'Prepare and submit ethics committee application',
            'status': 'in_progress',
            'priority': 'urgent',
            'deadline': datetime.now().date() + timedelta(days=15),
        },
        {
            'title': 'Stem Cell Culture Setup',
            'project': projects[5],
            'assigned_to': people[6],
            'description': 'Establish stem cell culture protocols',
            'status': 'todo',
            'priority': 'high',
            'deadline': datetime.now().date() + timedelta(days=40),
        }
    ]
    
    tasks = []
    for task_data in tasks_data:
        task = Task.objects.create(**task_data)
        tasks.append(task)
        print(f"  ✓ Created: {task.title} - {task.get_status_display()}")
    
    # Print summary
    print("\n" + "="*60)
    print("✅ DATA POPULATION COMPLETE!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  • Labs created: {Lab.objects.count()}")
    print(f"  • People created: {Person.objects.count()}")
    print(f"  • Projects created: {ResearchProject.objects.count()}")
    print(f"  • Tasks created: {Task.objects.count()}")
    print(f"\n🌐 Access the Lab Management module at: http://localhost:8002/labs/")
    print(f"👤 Admin credentials: admin / admin123")
    print("\n" + "="*60)

if __name__ == '__main__':
    create_synthetic_data()
