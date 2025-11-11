# User Service API Documentation

## Overview

The User Service is a Django-based microservice that manages user contact information (email, push tokens), notification preferences, login, and permissions. It exposes REST APIs for user data that can be consumed by the API Gateway and other services in the distributed notification system.

## Base URL
```
http://localhost:8000/auth/
```

## Response Format

All API responses follow a standardized format:

```json
{
  "success": boolean,
  "message": string,
  "data": object | array (optional),
  "error": string (optional),
  "meta": {
    "total": number,
    "limit": number,
    "page": number,
    "total_pages": number,
    "has_next": boolean,
    "has_previous": boolean
  } (optional, for paginated responses)
}
```

## API Endpoints

### Health Check

**Endpoint:** `GET /auth/health/`

**Description:** Health check endpoint for service monitoring

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Service is healthy",
  "data": {
    "status": "healthy",
    "database": "connected",
    "service": "user_service"
  }
}
```

---

### Authentication Endpoints

#### 1. User Registration

**Endpoint:** `POST /auth/register/`

**Description:** Register a new user account and automatically create notification preferences

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "role": "client",
  "phone_number": "+1234567890"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully. Please check your email for verification.",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "role": "client",
      "phone_number": "+1234567890",
      "is_verified": false,
      "date_joined": "2024-01-01T00:00:00Z"
    },
    "token": "your-auth-token-here"
  }
}
```

---

#### 2. User Login

**Endpoint:** `POST /auth/login/`

**Description:** Authenticate user and get access token

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "role": "client",
      "phone_number": "+1234567890",
      "is_verified": true,
      "date_joined": "2024-01-01T00:00:00Z"
    },
    "token": "your-auth-token-here"
  }
}
```

---

#### 3. User Logout

**Endpoint:** `POST /auth/logout/`

**Description:** Logout user and invalidate token

**Headers:**
```
Authorization: Token your-auth-token-here
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

#### 4. Get User Profile

**Endpoint:** `GET /auth/me/`

**Description:** Get current user's profile information

**Headers:**
```
Authorization: Token your-auth-token-here
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "client",
    "phone_number": "+1234567890",
    "is_verified": true,
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

---

#### 5. Update User Profile

**Endpoint:** `PUT /auth/me/` or `PATCH /auth/me/`

**Description:** Update current user's profile information

**Headers:**
```
Authorization: Token your-auth-token-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "newusername",
  "phone_number": "+9876543210"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User profile updated successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "newusername",
    "role": "client",
    "phone_number": "+9876543210",
    "is_verified": true,
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

---

### Push Token Management

#### 1. Register Push Token

**Endpoint:** `POST /auth/push-tokens/`

**Description:** Register a push notification token for the current user

**Headers:**
```
Authorization: Token your-auth-token-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "token": "fcm-token-or-onesignal-token-here",
  "device_type": "android",
  "device_id": "optional-device-id"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Push token registered successfully",
  "data": {
    "id": 1,
    "token": "fcm-token-or-onesignal-token-here",
    "device_type": "android",
    "device_id": "optional-device-id",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "last_used_at": null
  }
}
```

**Notes:**
- `device_type` can be: `android`, `ios`, or `web` (default: `web`)
- If the token already exists for the user, it will be updated instead of creating a new one
- Users can have multiple push tokens (for multiple devices)

---

#### 2. List Push Tokens

**Endpoint:** `GET /auth/push-tokens/`

**Description:** Get all push tokens for the current user

**Headers:**
```
Authorization: Token your-auth-token-here
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Push tokens retrieved successfully",
  "data": [
    {
      "id": 1,
      "token": "fcm-token-1",
      "device_type": "android",
      "device_id": "device-id-1",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "last_used_at": null
    },
    {
      "id": 2,
      "token": "fcm-token-2",
      "device_type": "ios",
      "device_id": "device-id-2",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "last_used_at": null
    }
  ],
  "meta": {
    "total": 2,
    "limit": 20,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

---

#### 3. Get Push Token

**Endpoint:** `GET /auth/push-tokens/{id}/`

**Description:** Get a specific push token

**Headers:**
```
Authorization: Token your-auth-token-here
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Push token retrieved successfully",
  "data": {
    "id": 1,
    "token": "fcm-token-here",
    "device_type": "android",
    "device_id": "device-id",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "last_used_at": null
  }
}
```

---

#### 4. Update Push Token

**Endpoint:** `PUT /auth/push-tokens/{id}/` or `PATCH /auth/push-tokens/{id}/`

**Description:** Update a push token

**Headers:**
```
Authorization: Token your-auth-token-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "device_type": "ios",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Push token updated successfully",
  "data": {
    "id": 1,
    "token": "fcm-token-here",
    "device_type": "ios",
    "device_id": "device-id",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T01:00:00Z",
    "last_used_at": null
  }
}
```

---

#### 5. Delete Push Token

**Endpoint:** `DELETE /auth/push-tokens/{id}/`

**Description:** Deactivate a push token (soft delete)

**Headers:**
```
Authorization: Token your-auth-token-here
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Push token deactivated successfully"
}
```

**Notes:**
- Tokens are not physically deleted, but marked as inactive
- Only the token owner can delete their own tokens

---

### Notification Preferences

#### 1. Get Notification Preferences

**Endpoint:** `GET /auth/notification-preferences/`

**Description:** Get current user's notification preferences

**Headers:**
```
Authorization: Token your-auth-token-here
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notification preferences retrieved successfully",
  "data": {
    "email_enabled": true,
    "email_marketing": true,
    "email_transactional": true,
    "email_security": true,
    "push_enabled": true,
    "push_marketing": true,
    "push_transactional": true,
    "push_security": true,
    "quiet_hours_enabled": false,
    "quiet_hours_start": null,
    "quiet_hours_end": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

#### 2. Update Notification Preferences

**Endpoint:** `PUT /auth/notification-preferences/` or `PATCH /auth/notification-preferences/`

**Description:** Update current user's notification preferences

**Headers:**
```
Authorization: Token your-auth-token-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "email_enabled": true,
  "email_marketing": false,
  "email_transactional": true,
  "email_security": true,
  "push_enabled": true,
  "push_marketing": false,
  "push_transactional": true,
  "push_security": true,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00:00",
  "quiet_hours_end": "08:00:00"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notification preferences updated successfully",
  "data": {
    "email_enabled": true,
    "email_marketing": false,
    "email_transactional": true,
    "email_security": true,
    "push_enabled": true,
    "push_marketing": false,
    "push_transactional": true,
    "push_security": true,
    "quiet_hours_enabled": true,
    "quiet_hours_start": "22:00:00",
    "quiet_hours_end": "08:00:00",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T01:00:00Z"
  }
}
```

---

### User Data Endpoints (for API Gateway and other services)

#### 1. List Users

**Endpoint:** `GET /auth/users/`

**Description:** List all users (admin only)

**Headers:**
```
Authorization: Token your-auth-token-here
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "phone_number": "+1234567890",
      "is_verified": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "total": 1,
    "limit": 20,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

---

#### 2. Get User Details

**Endpoint:** `GET /auth/users/{id}/`

**Description:** Get detailed user information including notification preferences and push tokens (for API Gateway)

**Headers:**
```
Authorization: Token your-auth-token-here
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User details retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "phone_number": "+1234567890",
    "is_verified": true,
    "notification_preferences": {
      "email_enabled": true,
      "email_marketing": true,
      "email_transactional": true,
      "email_security": true,
      "push_enabled": true,
      "push_marketing": true,
      "push_transactional": true,
      "push_security": true,
      "quiet_hours_enabled": false,
      "quiet_hours_start": null,
      "quiet_hours_end": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    "push_tokens": [
      {
        "id": 1,
        "token": "fcm-token-here",
        "device_type": "android",
        "device_id": "device-id",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "last_used_at": null
      }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Notes:**
- Users can only view their own data, unless they are admins
- Only active push tokens are returned
- This endpoint is designed for use by the API Gateway and other services

---

## Error Responses

All error responses follow the standard format:

```json
{
  "success": false,
  "message": "Error message describing what went wrong",
  "error": "Error code or detailed error message"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service is unhealthy

---

## Authentication

Most endpoints require authentication using Token-based authentication. Include the token in the Authorization header:

```
Authorization: Token your-auth-token-here
```

---

## Pagination

List endpoints support pagination using query parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

Paginated responses include a `meta` object with pagination information.

---

## Database Models

### User
- Manages user authentication and basic information
- Fields: `id`, `email`, `username`, `password`, `role`, `phone_number`, `is_verified`, `created_at`, `updated_at`

### PushToken
- Stores push notification tokens for users
- Supports multiple devices per user
- Fields: `id`, `user`, `token`, `device_type`, `device_id`, `is_active`, `created_at`, `updated_at`, `last_used_at`

### NotificationPreference
- Stores user notification preferences
- One-to-one relationship with User
- Fields: `user`, `email_enabled`, `email_marketing`, `email_transactional`, `email_security`, `push_enabled`, `push_marketing`, `push_transactional`, `push_security`, `quiet_hours_enabled`, `quiet_hours_start`, `quiet_hours_end`, `created_at`, `updated_at`

---

## Naming Conventions

All API requests and responses use `snake_case` for field names, as specified in the requirements.

---

## Integration with Other Services

### API Gateway
The User Service provides endpoints that can be consumed by the API Gateway:
- `GET /auth/users/{id}/` - Get user details with notification preferences and push tokens
- `GET /auth/users/` - List users (admin only)

### Email Service & Push Service
These services can query the User Service to:
- Get user email addresses
- Get user push tokens
- Check notification preferences
- Verify if notifications should be sent based on preferences and quiet hours

---

## Health Checks

The service exposes a `/auth/health/` endpoint that can be used for:
- Service discovery
- Load balancer health checks
- Monitoring and alerting

---

## Notes

- All timestamps are in UTC
- Email verification is required for full account access
- Password reset tokens are single-use and expire after 24 hours
- Authentication tokens are valid until logout or password change
- The service supports horizontal scaling
- Notification preferences are automatically created when a user registers
- Push tokens are soft-deleted (marked as inactive) when deleted

---

## Migration Instructions

To apply the database migrations for the new models:

```bash
python manage.py makemigrations auth_service
python manage.py migrate auth_service
```

This will create the following tables:
- `users` (already exists, may need migration for new fields)
- `push_tokens` (new)
- `notification_preferences` (new)
- `password_reset_tokens` (already exists)
- `email_verification_tokens` (already exists)

