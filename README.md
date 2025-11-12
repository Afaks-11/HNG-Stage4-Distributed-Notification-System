# Template & Email System (Role 3)

**Developer 3: Template & Email System Engineer**

This system manages notification templates and processes email notifications from a RabbitMQ queue.

## 🎯 My Responsibilities

- ✅ Manage notification templates (CRUD operations)
- ✅ Render templates with dynamic variables  
- ✅ Process email queue from RabbitMQ
- ✅ Send emails via SMTP

## 📁 Services

### Template Service (Port 3001)
- Stores and manages email templates
- Provides REST API for template CRUD
- Renders templates with variables

### Email Service (Port 3002)
- Consumes messages from Rabbit MQ `email.queue`
- Fetches templates from Template Service
- Sends emails via Gmail SMTP

## 🚀 Quick Start

```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Start Template Service
cd template-email-service/template-service
pnpm install
pnpm run start:dev

# 3. Start Email Service  
cd ../email-service
pnpm install
pnpm run start:dev

# 4. Run test
npx ts-node test-integration.ts
```

## 📡 API Endpoints

### Create Template
```bash
POST http://localhost:3001/api/v1/templates
{
  "code": "welcome_email",
  "name": "Welcome Email",
  "subject": "Welcome {{name}}!",
  "body": "<h1>Hello {{name}}</h1>"
}
```

### Get Template
```bash
GET http://localhost:3001/api/v1/templates/by-code/welcome_email
```

### Send Email (via RabbitMQ)
```json
{
  "template_code": "welcome_email",
  "variables": {
    "name": "John",
    "email": "john@example.com"
  },
  "request_id": "req-123"
}
```

## 🐳 Infrastructure

- **RabbitMQ**: localhost:5672 (UI: localhost:15672)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

Login: `admin / admin123`
