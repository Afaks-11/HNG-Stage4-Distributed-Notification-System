# Quick Start Guide

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment file
cp env.example .env

# Edit .env and set at minimum:
# - DB_NAME, DB_USER, DB_PASSWORD (PostgreSQL credentials)
# - SECRET_KEY (generate a new one)
```

### 3. Set Up Database

```bash
# Create PostgreSQL database
createdb user_service_db

# Or using psql:
psql -U postgres -c "CREATE DATABASE user_service_db;"
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000/auth/health/

## Test the API

### Health Check
```bash
curl http://localhost:8000/auth/health/
```

### Register User
```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "role": "client"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

## Project Structure

```
.
├── auth_service/          # User Service Django app
│   ├── models.py         # User, PushToken, NotificationPreference models
│   ├── views.py          # API views
│   ├── serializers.py    # DRF serializers
│   └── urls.py           # App URLs
├── user_service/         # Django project
│   ├── settings.py       # Django settings
│   └── urls.py           # Project URLs
├── manage.py             # Django management
└── requirements.txt      # Dependencies
```

## Next Steps

1. Read `README_SETUP.md` for detailed setup instructions
2. Read `auth_service/USER_SERVICE_API.md` for API documentation
3. Configure email settings in `.env` for verification emails
4. Set up Redis (optional) for caching

## Common Issues

**Database connection error**: Make sure PostgreSQL is running and credentials in `.env` are correct.

**Migration errors**: Run `python manage.py migrate` after setting up the database.

**Import errors**: Make sure you've activated the virtual environment and installed requirements.

