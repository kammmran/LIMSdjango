# Lab Management System (LIMS) Module - Setup & Usage Guide

## Overview

A comprehensive Lab Management System has been successfully integrated into your LIMS application. This module provides complete management of laboratories, research projects, people, and tasks with a clean, modern, and intuitive UI.

## Features Implemented

### 1. **Labs Management**
- List all laboratories and research groups
- Create, view, edit, and delete labs
- Lab details include:
  - Name, code, description, location
  - Head of lab
  - Research focus area
  - Number of members and active projects
- Lab detail page with tabs: Overview, Members, Projects, Tasks

### 2. **People Management**
- Complete people/team member management
- Roles: Lab Manager, Researcher, Assistant, Student
- Person profile includes:
  - Contact information (email, phone)
  - ORCID identifier
  - Skills (comma-separated)
  - Lab assignment
  - Active/inactive status
  - Photo upload
- Grid view with filter by role and lab

### 3. **Research Projects**
- Full project lifecycle management
- Project information:
  - Title, summary
  - Principal Investigator
  - Team members
  - Start/end dates
  - Status: Active, Completed, On Hold
  - Priority levels
  - Funding source and budget
  - File attachments (PDF, Excel, etc.)
- Project detail page with tasks and attachments

### 4. **Task Management**
- Task tracking for labs and projects
- Fields: title, description, assigned to, priority, status, deadline
- **Kanban Board View** (To Do / In Progress / Done)
- Drag-and-drop-like status updates via buttons
- Table list view with filters
- Overdue task indicators

### 5. **Dashboard**
- High-level overview with statistics:
  - Number of active labs
  - Team member count
  - Active projects count
  - Tasks by status
- Upcoming deadlines widget
- Recent projects list
- Quick action buttons

### 6. **UI/UX Design**
- Clean, minimalistic layout
- Soft color palette with gradient accents
- Responsive design (mobile-friendly)
- Card-based layouts
- Tab navigation for grouped information
- Search and filter capabilities
- Breadcrumb navigation
- Status badges and priority indicators

## Installation Steps

### 1. Database Migration

Run the following commands to create database tables:

```bash
python manage.py makemigrations labs
python manage.py migrate labs
```

### 2. Create Initial Data (Optional)

You can create sample data through the Django admin or create a fixture file. Here's a quick script to add sample data:

```python
# In Django shell: python manage.py shell
from labs.models import Lab, Person, ResearchProject, Task
from datetime import date, timedelta

# Create a lab
lab = Lab.objects.create(
    name="Molecular Biology Lab",
    code="MBL-001",
    description="Research in molecular biology and genetics",
    location="Building A, Floor 3",
    research_focus="Gene expression and regulation",
    established_date=date(2020, 1, 1),
    is_active=True
)

# Create people
person1 = Person.objects.create(
    first_name="Dr. Jane",
    last_name="Smith",
    email="jane.smith@lab.com",
    role="lab_manager",
    position="Senior Researcher",
    lab=lab,
    is_active=True
)

# Create a project
project = ResearchProject.objects.create(
    lab=lab,
    title="Gene Expression Study",
    summary="Investigating gene expression patterns in cancer cells",
    principal_investigator=person1,
    start_date=date.today(),
    status="active",
    priority="high"
)
project.team_members.add(person1)

# Create a task
task = Task.objects.create(
    title="Literature Review",
    description="Review recent publications on gene expression",
    lab=lab,
    project=project,
    assigned_to=person1,
    status="todo",
    priority="high",
    deadline=date.today() + timedelta(days=7)
)
```

### 3. Access the Module

Navigate to: `http://localhost:8000/labs/`

## URL Routes

- **Dashboard**: `/labs/`
- **Labs**:
  - List: `/labs/labs/`
  - Detail: `/labs/labs/<id>/`
  - Create: `/labs/labs/create/`
  - Edit: `/labs/labs/<id>/update/`
  - Delete: `/labs/labs/<id>/delete/`

- **People**:
  - List: `/labs/people/`
  - Detail: `/labs/people/<id>/`
  - Create: `/labs/people/create/`
  - Edit: `/labs/people/<id>/update/`
  - Delete: `/labs/people/<id>/delete/`

- **Projects**:
  - List: `/labs/projects/`
  - Detail: `/labs/projects/<id>/`
  - Create: `/labs/projects/create/`
  - Edit: `/labs/projects/<id>/update/`
  - Delete: `/labs/projects/<id>/delete/`

- **Tasks**:
  - List: `/labs/tasks/`
  - Kanban Board: `/labs/tasks/kanban/`
  - Detail: `/labs/tasks/<id>/`
  - Create: `/labs/tasks/create/`
  - Edit: `/labs/tasks/<id>/update/`
  - Delete: `/labs/tasks/<id>/delete/`

## Navigation

The Lab Management System is accessible from the left sidebar under "Lab Management" section with links to:
- Labs Dashboard
- Laboratories
- People
- Projects
- Tasks

## Key Features & Workflows

### Creating a New Lab
1. Navigate to "Laboratories" from sidebar
2. Click "New Lab" button
3. Fill in required fields (Name, Code)
4. Optionally assign a head of lab
5. Save

### Managing People
1. Go to "People" section
2. Click "Add Person"
3. Enter personal and professional details
4. Assign to a lab
5. Add skills (comma-separated)
6. Upload photo (optional)

### Creating Research Projects
1. Navigate to "Projects"
2. Click "New Project"
3. Select lab
4. Enter project details
5. Assign Principal Investigator
6. Select team members (hold Ctrl/Cmd for multiple)
7. Set timeline and status

### Using the Kanban Board
1. Go to "Tasks" > "Kanban View"
2. View tasks organized by status (To Do, In Progress, Done)
3. Click status buttons to move tasks between columns
4. Tasks automatically update via AJAX
5. View overdue indicators

### Managing Project Attachments
1. Open a project detail page
2. Click "Upload" in the Attachments section
3. Select file (PDF, Excel, etc.)
4. Add title and description
5. Upload

## Styling & Customization

The module uses a dedicated CSS file at `/static/css/labs.css` with:
- Gradient color schemes for status cards
- Responsive grid layouts
- Card-based design system
- Badge styling for statuses and priorities
- Kanban board styling
- Tab navigation

### Color Scheme
- **Primary**: Blue (#007bff)
- **Success**: Green (#28a745)
- **Warning**: Yellow (#ffc107)
- **Danger**: Red (#dc3545)
- **Gradients**: Various gradient combinations for visual appeal

## Admin Interface

All models are registered in Django admin with:
- Custom list displays
- Search capabilities
- Filtering options
- Field grouping
- Read-only timestamp fields

Access admin at: `http://localhost:8000/admin/`

## Models Structure

### Lab
- Basic info (name, code, description, location)
- Head of lab (ForeignKey to Person)
- Research focus
- Active status
- Timestamps

### Person
- Personal details (name, email, phone, photo)
- Professional info (position, role, ORCID, skills)
- Lab assignment (ForeignKey to Lab)
- Active status
- Timestamps

### ResearchProject
- Project details (title, summary)
- Lab (ForeignKey)
- PI and team members (ForeignKey and ManyToMany to Person)
- Timeline (start/end dates)
- Status and priority
- Funding information
- Notes
- Timestamps

### Task
- Task info (title, description)
- Lab and project assignments (ForeignKeys)
- Assigned to (ForeignKey to Person)
- Status (todo, in_progress, done)
- Priority (low, medium, high, urgent)
- Deadline
- Timestamps

### ProjectAttachment
- Project (ForeignKey)
- File upload
- Title, description
- Uploaded by (ForeignKey to Person)
- Timestamp

## Best Practices

1. **Always assign people to labs** for better organization
2. **Use the Kanban board** for visual task management
3. **Set realistic deadlines** to track overdue tasks
4. **Upload project documentation** using attachments feature
5. **Use filters and search** to quickly find items
6. **Assign proper roles** to people for clarity
7. **Keep project summaries** concise but informative

## Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic
```

### Tabs not working
- Ensure jQuery and Bootstrap JS are loaded
- Check browser console for JavaScript errors

### Images not displaying
- Check MEDIA_URL and MEDIA_ROOT settings
- Ensure media files are served in development

## Future Enhancements

Potential features to add:
- Real drag-and-drop for Kanban board
- Email notifications for task assignments
- Project Gantt chart timeline view
- Export functionality for projects and tasks
- Integration with calendar for deadlines
- Advanced analytics and reporting
- Collaboration features (comments, notes)

## Support

For questions or issues:
1. Check model field constraints
2. Review Django admin for data validation
3. Check browser console for frontend errors
4. Review Django logs for backend issues

---

**Module Created**: November 2025
**Django Version**: 5.0+
**Status**: Production Ready ✅
