import pika
import json

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost',
    port=5672,
    credentials=pika.PlainCredentials('admin', 'admin123')
))
channel = connection.channel()

# Ensure queue exists
channel.queue_declare(queue='email.queue', durable=True)

# Test email message
email_message = {
    "notification_type": "email",
    "user_id": "user-123",
    "template_code": "welcome_email",
    "variables": {
        "name": "John Doe",
        "email": "test@example.com"
    },
    "request_id": "test-email-123"
}

print("📨 Sending email message to queue...")
print(json.dumps(email_message, indent=2))

# Send message to queue
channel.basic_publish(
    exchange='',
    routing_key='email.queue',
    body=json.dumps(email_message),
    properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
)

print("✅ Email message sent to queue!")
print("📬 Check email service logs to see processing...")

connection.close()