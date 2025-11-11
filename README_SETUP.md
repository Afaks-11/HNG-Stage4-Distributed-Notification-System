# User Service Setup Guide

This guide will help you set up and run the User Service for the Distributed Notification System.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis (optional, for caching)
- pip (Python package manager)

## Installation Steps

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the `env.example` file to `.env` and update the values:

```bash
cp env.example .env
```

Edit `.env` and configure:
- Database credentials (PostgreSQL)
- Redis settings (if using)
- Email settings (for sending verification emails)
- Secret key (generate a new one for production)

### 4. Set Up PostgreSQL Database

Create a PostgreSQL database:

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE user_service_db;

# Create user (optional)
CREATE USER user_service_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE user_service_db TO user_service_user;
\q
```

Update your `.env` file with the database credentials.

### 5. Run Migrations

```bash
python manage.py migrate
```

This will create all the necessary database tables:
- `users`
- `push_tokens`
- `notification_preferences`
- `password_reset_tokens`
- `email_verification_tokens`

### 6. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

This will allow you to access the Django admin interface.

### 7. Run the Development Server

```bash
python manage.py runserver
```

The service will be available at `http://localhost:8000`

## Project Structure

```
.
├── auth_service/          # Django app (User Service)
│   ├── models.py         # Database models
│   ├── views.py          # API views
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # URL routing
│   ├── admin.py          # Django admin configuration
│   └── ...
├── user_service/         # Django project
│   ├── settings.py       # Django settings
│   ├── urls.py           # Project URLs
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
└── .env.example          # Example environment variables
```

## API Endpoints

The service exposes endpoints under `/auth/`:

- `GET /auth/health/` - Health check
- `POST /auth/register/` - User registration
- `POST /auth/login/` - User login
- `GET /auth/me/` - Get user profile
- `GET /auth/push-tokens/` - List push tokens
- `POST /auth/push-tokens/` - Register push token
- `GET /auth/notification-preferences/` - Get notification preferences
- `PUT /auth/notification-preferences/` - Update notification preferences
- `GET /auth/users/` - List users (admin only)
- `GET /auth/users/{id}/` - Get user details

See `auth_service/USER_SERVICE_API.md` for detailed API documentation.

## Configuration

### Database

The service uses PostgreSQL. Configure in `.env`:

```env
DB_NAME=user_service_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### Redis (Optional)

Redis is used for caching. To enable, set in `.env`:

```env
USE_REDIS=True
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

If Redis is not available, the service will use local memory cache.

### Email

Configure email settings in `.env` for sending verification and password reset emails:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

For Gmail, you'll need to generate an App Password:
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"

## Testing

Run the test suite:

```bash
python manage.py test auth_service
```

## Making Migrations

If you modify models, create migrations:

```bash
python manage.py makemigrations auth_service
python manage.py migrate
```

## Docker (Optional)

If you prefer to use Docker, you can create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: user_service_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DB_HOST=db
      - REDIS_HOST=redis

volumes:
  postgres_data:
```

## Troubleshooting

### Database Connection Error

- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists: `psql -U postgres -l`

### Migration Errors

- Make sure you've run `python manage.py migrate` after setting up the database
- If you get "table already exists" errors, you may need to reset migrations (development only)

### Redis Connection Error

- Redis is optional - the service will use local memory cache if Redis is not available
- To disable Redis, set `USE_REDIS=False` in `.env`

### Email Not Sending

- Check email credentials in `.env`
- For Gmail, ensure you're using an App Password, not your regular password
- Check that `EMAIL_USE_TLS=True` for Gmail

## Production Deployment

For production:

1. Set `DEBUG=False` in `.env`
2. Generate a new `SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain
4. Set up a proper email backend (SendGrid, AWS SES, etc.)
5. Use a production-grade WSGI server (Gunicorn, uWSGI)
6. Set up proper database backups
7. Configure HTTPS
8. Set up monitoring and logging

## Support

For issues or questions, refer to the API documentation in `auth_service/USER_SERVICE_API.md`.

