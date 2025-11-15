# Django LIMS - Laboratory Information Management System

A complete, modern, and fully-featured Laboratory Information Management System built with Django.

## Features

### Core Modules
- **Dashboard**: Real-time metrics, charts, and activity feed
- **Sample Management**: Register, track, and manage laboratory samples
- **Test Management**: Define test types, assign tests, track workflow
- **Results Management**: Enter, review, and approve test results
- **Inventory**: Manage reagents, chemicals, and stock items
- **Instruments**: Track instruments, calibration, and maintenance
- **Reports**: Generate comprehensive reports with export capabilities
- **Audit Logs**: Complete system activity tracking
- **User & Role Management**: Advanced permissions and access control

### UI/UX Features
- Clean, minimalistic, and professional design
- Responsive layout (Desktop, Tablet, Mobile)
- Modern flat design with laboratory-appropriate styling
- Intuitive navigation with sidebar menu
- Real-time search and filtering
- Interactive dashboards with charts
- Status badges and visual indicators

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Quick Start

1. **Clone or download the project**
   ```bash
   cd /Users/narmak/Downloads/lims
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # OR
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

6. **Load initial data (optional)**
   ```bash
   python manage.py shell
   ```
   Then run:
   ```python
   from users.models import Role
   
   # Create default roles
   Role.objects.create(
       name='admin',
       description='System Administrator',
       can_register_samples=True,
       can_assign_tests=True,
       can_enter_results=True,
       can_approve_results=True,
       can_manage_inventory=True,
       can_manage_instruments=True,
       can_view_reports=True,
       can_manage_users=True
   )
   
   Role.objects.create(
       name='lab_manager',
       description='Laboratory Manager',
       can_register_samples=True,
       can_assign_tests=True,
       can_enter_results=True,
       can_approve_results=True,
       can_manage_inventory=True,
       can_manage_instruments=True,
       can_view_reports=True
   )
   
   Role.objects.create(
       name='technician',
       description='Laboratory Technician',
       can_register_samples=True,
       can_assign_tests=True,
       can_enter_results=True,
       can_view_reports=True
   )
   
   Role.objects.create(
       name='reviewer',
       description='Results Reviewer',
       can_approve_results=True,
       can_view_reports=True
   )
   
   exit()
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and go to: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin
   - Login with your superuser credentials

## Project Structure

```
lims/
├── lims_project/           # Main project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py             # WSGI configuration
│
├── dashboard/              # Dashboard app
├── samples/                # Sample management
├── tests/                  # Test management
├── results/                # Results management
├── inventory/              # Inventory management
├── instruments/            # Instrument management
├── reports/                # Reporting module
├── audit/                  # Audit logging
├── users/                  # User & authentication
│
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── dashboard/          # Dashboard templates
│   ├── samples/            # Sample templates
│   ├── tests/              # Test templates
│   ├── results/            # Results templates
│   ├── inventory/          # Inventory templates
│   ├── instruments/        # Instrument templates
│   ├── reports/            # Report templates
│   ├── audit/              # Audit templates
│   └── users/              # User templates
│
├── static/                 # Static files
│   ├── css/                # Stylesheets
│   │   └── style.css       # Main stylesheet
│   └── js/                 # JavaScript files
│       └── main.js         # Main JavaScript
│
├── media/                  # User-uploaded files
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Usage Guide

### 1. User Management
- Navigate to **Users & Roles** in the sidebar (admin only)
- Create users and assign roles
- Each role has specific permissions

### 2. Sample Registration
- Go to **Samples → Register New Sample**
- Fill in sample details (type, source, priority, etc.)
- Sample ID is auto-generated
- Attach files if needed

### 3. Test Assignment
- Go to **Tests → Assign Tests**
- Select a sample
- Choose test types to assign
- Assign to a technician

### 4. Test Workflow
- View **Tests → Test Workflow** for kanban-style view
- Tests move through: Assigned → In Progress → Waiting Review → Completed

### 5. Results Entry
- Go to **Results → Enter Results**
- Select a test assignment
- Enter parameter values
- Upload instrument files
- Save as draft or submit for review

### 6. Results Approval
- Reviewers go to **Results → Pending Review**
- Review entered results
- Approve or reject with comments

### 7. Inventory Management
- **Inventory → Reagents**: Manage chemicals and reagents
- **Inventory → Stock Items**: Track consumables
- **Inventory → Low Stock Alerts**: View items needing reorder
- System tracks expiry dates and minimum quantities

### 8. Instrument Management
- **Instruments → Instrument List**: View all instruments
- Add calibration records
- Log maintenance activities
- Track calibration due dates

### 9. Reports
- **Reports → Dashboard**: Select report type
- Apply filters (date range, type, status, etc.)
- Preview results
- Export as CSV/Excel

### 10. Audit Trail
- **Audit Log**: View all system activities
- Filter by user, action, date, model
- Complete transparency for compliance

## Configuration

### Database
The default configuration uses SQLite for development. For production, update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lims_db',
        'USER': 'lims_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Email (for password reset)
Update in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_password'
```

### Static Files (for production)
```bash
python manage.py collectstatic
```

## Security Considerations

### Before Production:
1. Change `SECRET_KEY` in `settings.py`
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Use environment variables for sensitive data
5. Enable HTTPS
6. Configure CSRF and CORS settings
7. Set up proper database backups

## Testing

Run tests:
```bash
python manage.py test
```

## Deployment

### Using Gunicorn (Production)
```bash
gunicorn lims_project.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker (Optional)
Create a `Dockerfile` and `docker-compose.yml` for containerized deployment.

## Support & Documentation

- Django Documentation: https://docs.djangoproject.com/
- Project Issues: Report bugs and request features

## License

This project is provided as-is for educational and commercial use.

## Credits

Built with Django 5.0 and modern web technologies.
Designed following laboratory industry standards and best practices.

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Developer**: LIMS Development Team
