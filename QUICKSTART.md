# QUICK START GUIDE - Django LIMS

## Immediate Next Steps

### 1. Install Django (if not already installed)
```bash
pip install django
```

### 2. Navigate to project directory
```bash
cd /Users/narmak/Downloads/lims
```

### 3. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Create database and run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser account
```bash
python manage.py createsuperuser
```
Enter your desired username, email, and password.

### 7. Run development server
```bash
python manage.py runserver
```

### 8. Access the application
Open browser: http://127.0.0.1:8000/auth/login/

---

## Project Overview

This is a complete **Laboratory Information Management System (LIMS)** with:

✅ **9 Django apps** fully configured
✅ **Complete database models** for all modules  
✅ **Modern UI/UX** with responsive design
✅ **User authentication** with role-based permissions
✅ **Full CRUD operations** for samples, tests, results, inventory, instruments
✅ **Dashboard** with metrics and charts
✅ **Audit logging** for compliance
✅ **Reports** with CSV export

---

## Key Features by Module

### 1. Dashboard (`/dashboard/`)
- Real-time metrics cards
- Weekly sample count chart
- Test categories pie chart
- Recent activity feed
- Quick links to common actions

### 2. Samples (`/samples/`)
- Register new samples (auto-generated IDs)
- List samples with advanced filtering
- View sample details with tabs
- Upload attachments
- Track sample lifecycle

### 3. Tests (`/tests/`)
- Define test types with parameters
- Assign tests to samples
- Kanban workflow board
- Track test status progression

### 4. Results (`/results/`)
- Enter parameter results
- Upload instrument files
- Submit for review
- Approve/reject workflow
- Export approved results

### 5. Inventory (`/inventory/`)
- Manage reagents and chemicals
- Track stock items
- Low stock alerts
- Expiry date monitoring

### 6. Instruments (`/instruments/`)
- Instrument registry
- Calibration tracking
- Maintenance logs
- Calibration reminders

### 7. Reports (`/reports/`)
- Sample reports
- Test reports
- Inventory reports
- Instrument reports
- CSV export functionality

### 8. Audit Log (`/audit/`)
- Complete activity tracking
- Filter by user, action, date
- Compliance and transparency

### 9. Users (`/users/`)
- User management
- Role-based permissions
- Profile management
- Password reset functionality

---

## Default Login Credentials

After creating superuser, you can:
1. Login with your superuser credentials
2. Create additional users via `/users/list/`
3. Create roles via `/users/roles/`
4. Assign permissions to roles

---

## File Structure Summary

```
lims/
├── manage.py                 # Django CLI
├── requirements.txt          # Dependencies
├── SETUP_GUIDE.md           # Full documentation
├── lims_project/            # Main settings
├── dashboard/               # Dashboard app
├── samples/                 # Sample management
├── tests/                   # Test management
├── results/                 # Results management
├── inventory/               # Inventory management
├── instruments/             # Instrument management
├── reports/                 # Reporting
├── audit/                   # Audit logging
├── users/                   # Authentication
├── templates/               # HTML templates
└── static/                  # CSS/JS files
```

---

## Common Commands

### Create migrations
```bash
python manage.py makemigrations
```

### Apply migrations
```bash
python manage.py migrate
```

### Create superuser
```bash
python manage.py createsuperuser
```

### Run development server
```bash
python manage.py runserver
```

### Access admin panel
http://127.0.0.1:8000/admin/

### Collect static files (production)
```bash
python manage.py collectstatic
```

---

## Troubleshooting

### Import errors for Django
**Solution:** Make sure Django is installed:
```bash
pip install django
```

### Database errors
**Solution:** Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static files not loading
**Solution:** Ensure DEBUG=True in settings.py for development

### Port already in use
**Solution:** Use different port:
```bash
python manage.py runserver 8001
```

---

## Next Steps After Setup

1. **Create Roles**: Go to Users → Roles and create:
   - Administrator
   - Lab Manager
   - Technician
   - Reviewer

2. **Add Users**: Create users and assign roles

3. **Configure Test Types**: Go to Tests → Test Types and add your lab tests

4. **Add Instruments**: Register your laboratory instruments

5. **Setup Inventory**: Add reagents and stock items

6. **Start Using**: Register samples and begin workflow!

---

## Production Deployment

See `SETUP_GUIDE.md` for detailed production deployment instructions including:
- Database configuration (PostgreSQL)
- Static file serving
- Security settings
- Email configuration
- HTTPS setup

---

## Support

For issues or questions:
1. Check SETUP_GUIDE.md for detailed documentation
2. Review Django documentation: https://docs.djangoproject.com/
3. Check error messages in terminal

---

**Version:** 1.0.0  
**Built with:** Django 5.0, Python 3.10+  
**License:** MIT
