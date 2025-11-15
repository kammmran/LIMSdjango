# Heroku Deployment Guide for LIMS

## Prerequisites
- Git installed
- Heroku CLI installed (`brew tap heroku/brew && brew install heroku`)
- A Heroku account

## Deployment Steps

### 1. Install Heroku CLI (if not already installed)
```bash
brew tap heroku/brew && brew install heroku
```

### 2. Login to Heroku
```bash
heroku login
```

### 3. Initialize Git Repository (if not already done)
```bash
git init
git add .
git commit -m "Initial commit"
```

### 4. Create Heroku App
```bash
heroku create your-lims-app-name
# Or let Heroku generate a random name:
# heroku create
```

### 5. Add PostgreSQL Database
```bash
heroku addons:create heroku-postgresql:mini
```

### 6. Set Environment Variables
```bash
# Generate a secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Set the secret key
heroku config:set SECRET_KEY='your-generated-secret-key'

# Set other variables
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS='.herokuapp.com'
```

### 7. Deploy to Heroku
```bash
git push heroku main
# Or if your branch is named 'master':
# git push heroku master
```

### 8. Run Database Migrations
```bash
heroku run python manage.py migrate
```

### 9. Create Superuser
```bash
heroku run python manage.py createsuperuser
```

### 10. Collect Static Files (if needed)
```bash
heroku run python manage.py collectstatic --noinput
```

### 11. Open Your App
```bash
heroku open
```

## Viewing Logs
```bash
heroku logs --tail
```

## Running Commands on Heroku
```bash
heroku run python manage.py <command>
```

## Scaling Dynos
```bash
# Check current dyno status
heroku ps

# Scale web dynos
heroku ps:scale web=1
```

## Database Management

### Access Database Shell
```bash
heroku run python manage.py dbshell
```

### Backup Database
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

### Reset Database (CAUTION: This will delete all data!)
```bash
heroku pg:reset DATABASE_URL
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

## Environment Variables

### View all config vars
```bash
heroku config
```

### Set a config var
```bash
heroku config:set VARIABLE_NAME=value
```

### Unset a config var
```bash
heroku config:unset VARIABLE_NAME
```

## Local Testing with Heroku Settings

You can test your app locally with production-like settings:

1. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

2. Edit `.env` with your local settings:
```
SECRET_KEY=your-local-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

3. Run locally:
```bash
python manage.py runserver
```

## Troubleshooting

### Application Error
Check logs:
```bash
heroku logs --tail
```

### Static Files Not Loading
```bash
heroku run python manage.py collectstatic --noinput
```

### Database Issues
```bash
heroku run python manage.py migrate
heroku restart
```

### Reset and Redeploy
```bash
git add .
git commit -m "Update"
git push heroku main
heroku restart
```

## Production Checklist

- [ ] SECRET_KEY is set and unique
- [ ] DEBUG is set to False
- [ ] ALLOWED_HOSTS includes your Heroku domain
- [ ] Database migrations are up to date
- [ ] Static files are collected
- [ ] Superuser account created
- [ ] HTTPS is enforced (automatic on Heroku)
- [ ] Environment variables are set correctly
- [ ] Media files storage is configured (consider AWS S3 for production)

## Cost Considerations

- **Eco Dynos**: $5/month (recommended for small apps)
- **Mini PostgreSQL**: $5/month
- **Total**: ~$10/month for a small production setup

Free tier is available but dynos sleep after 30 minutes of inactivity.

## Continuous Deployment

You can connect your Heroku app to a GitHub repository for automatic deployments:

1. Go to your app dashboard on heroku.com
2. Click on the "Deploy" tab
3. Connect to GitHub
4. Enable automatic deploys from your main branch

## Additional Resources

- [Heroku Django Documentation](https://devcenter.heroku.com/articles/django-app-configuration)
- [Heroku Postgres](https://devcenter.heroku.com/articles/heroku-postgresql)
- [Heroku CLI Reference](https://devcenter.heroku.com/articles/heroku-cli)
