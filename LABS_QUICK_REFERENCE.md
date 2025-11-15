# Lab Management System - Quick Reference

## Quick Start Commands

### 1. Run Migrations
```bash
python manage.py makemigrations labs
python manage.py migrate labs
```

### 2. Create Superuser (if not already created)
```bash
python manage.py createsuperuser
```

### 3. Run Development Server
```bash
python manage.py runserver
```

### 4. Access the Application
- **Main Dashboard**: http://localhost:8000/
- **Labs Module**: http://localhost:8000/labs/
- **Admin Interface**: http://localhost:8000/admin/

## Navigation Quick Links

| Feature | URL | Description |
|---------|-----|-------------|
| Labs Dashboard | `/labs/` | Main overview with stats |
| Labs List | `/labs/labs/` | All laboratories |
| People List | `/labs/people/` | Team members |
| Projects List | `/labs/projects/` | Research projects |
| Task Kanban | `/labs/tasks/kanban/` | Visual task board |
| Task List | `/labs/tasks/` | Table view of tasks |

## Common Workflows

### Add a New Lab
1. Click "Laboratories" in sidebar
2. Click "New Lab"
3. Fill: Name, Code (required)
4. Add location, description, research focus (optional)
5. Click "Save Lab"

### Add a Person
1. Click "People" in sidebar
2. Click "Add Person"
3. Fill: First Name, Last Name, Email (required)
4. Select role and lab
5. Add skills, ORCID (optional)
6. Click "Save Person"

### Create a Project
1. Click "Projects" in sidebar
2. Click "New Project"
3. Fill: Title, Lab (required)
4. Add summary, PI, team members
5. Set dates, status, priority
6. Click "Save Project"

### Create a Task
1. Click "Tasks" in sidebar
2. Click "New Task"
3. Fill: Title (required)
4. Select lab or project
5. Assign to person
6. Set priority and deadline
7. Click "Save Task"

### Move Task on Kanban
1. Go to Tasks → Kanban View
2. Find task card
3. Click move button (e.g., "Move to In Progress")
4. Task updates automatically

## Model Fields Reference

### Lab Fields
- **name*** - Lab name
- **code*** - Unique identifier (e.g., LAB-001)
- **description** - Lab description
- **location** - Building/room
- **head_of_lab** - Person in charge
- **research_focus** - Main research areas
- **established_date** - When lab was created
- **is_active** - Active/inactive status

### Person Fields
- **first_name*** - First name
- **last_name*** - Last name
- **email*** - Email address (unique)
- **phone** - Phone number
- **position** - Job title
- **role*** - Lab Manager, Researcher, Assistant, Student
- **orcid** - ORCID identifier
- **skills** - Comma-separated list
- **lab** - Assigned laboratory
- **is_active** - Active/inactive
- **joined_date** - When joined
- **photo** - Profile picture

### Project Fields
- **lab*** - Laboratory
- **title*** - Project title
- **summary** - Project description
- **principal_investigator** - PI
- **team_members** - Multiple people
- **start_date** - Start date
- **end_date** - End date
- **status*** - active, completed, on_hold
- **priority** - low, medium, high
- **funding_source** - Funding organization
- **budget** - Project budget
- **notes** - Additional notes

### Task Fields
- **title*** - Task title
- **description** - Task details
- **lab** - Associated lab
- **project** - Associated project
- **assigned_to** - Person assigned
- **status*** - todo, in_progress, done
- **priority*** - low, medium, high, urgent
- **deadline** - Due date

## Status & Priority Badges

### Project Status
- 🔵 **Active** - Ongoing project
- 🟢 **Completed** - Finished project
- ⚫ **On Hold** - Paused project

### Task Status
- ⚪ **To Do** - Not started
- 🔵 **In Progress** - Currently working
- 🟢 **Done** - Completed

### Priority Levels
- 🔵 **Low** - Can wait
- 🟡 **Medium** - Normal priority
- 🟠 **High** - Important
- 🔴 **Urgent** - Critical

## Keyboard Shortcuts

*(Note: These would need to be implemented with JavaScript)*

- `Ctrl/Cmd + K` - Global search
- `L` - Go to Labs list
- `P` - Go to People list
- `R` - Go to Projects list
- `T` - Go to Tasks
- `K` - Kanban view
- `N` - Create new (depends on current page)

## Filters & Search

### Labs List
- Search: Name, Code, Location
- No additional filters

### People List
- Search: Name, Email
- Filter by: Role, Lab, Active status

### Projects List
- Search: Title, Summary
- Filter by: Status, Lab

### Tasks List
- Search: Title, Description
- Filter by: Status, Priority

## Tips & Tricks

✅ **Use breadcrumbs** for easy navigation back
✅ **Hover over cards** for subtle animations
✅ **Use Kanban board** for visual task management
✅ **Check dashboard** for quick overview
✅ **Filter people by lab** to see team composition
✅ **Upload attachments** to projects for documentation
✅ **Set deadlines** to track task urgency
✅ **Use skills field** to track expertise

## Common Issues

### Problem: Can't see labs in dropdown
**Solution**: Create labs first before assigning to people/projects

### Problem: Tabs not switching
**Solution**: Ensure jQuery and Bootstrap JS are loaded. Check browser console.

### Problem: Static files not loading
**Solution**: Run `python manage.py collectstatic`

### Problem: Media files not displaying
**Solution**: Check MEDIA_URL and MEDIA_ROOT in settings.py

### Problem: Permission denied
**Solution**: Ensure user is logged in and has proper permissions

## Admin Functions

Access Django Admin at `/admin/`

**Available Models:**
- Labs → Manage all laboratories
- People → Manage all persons
- Research Projects → Manage projects
- Tasks → Manage tasks
- Project Attachments → View/manage uploads

**Admin Features:**
- Bulk actions
- Advanced filtering
- Search functionality
- Field validation
- Related object links

## API Endpoints (if REST API is added later)

Currently, the module uses Django views. To add REST API:
1. Install Django REST Framework
2. Create serializers for each model
3. Create API views/viewsets
4. Add API URLs

Example future endpoint structure:
```
GET    /api/labs/                  - List labs
POST   /api/labs/                  - Create lab
GET    /api/labs/{id}/             - Lab detail
PUT    /api/labs/{id}/             - Update lab
DELETE /api/labs/{id}/             - Delete lab
GET    /api/labs/{id}/members/     - Lab members
GET    /api/labs/{id}/projects/    - Lab projects
```

## Backup & Data Export

### Export from Admin
1. Go to Django Admin
2. Select items
3. Choose "Export selected items" (if installed)

### Backup Database
```bash
python manage.py dumpdata labs > labs_backup.json
```

### Restore Database
```bash
python manage.py loaddata labs_backup.json
```

---

**Last Updated**: November 2025
**Version**: 1.0
