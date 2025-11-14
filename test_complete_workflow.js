const amqp = require('amqplib');

async function testCompleteWorkflow() {
  try {
    console.log('🚀 Starting complete workflow test...\n');

    // Connect to RabbitMQ
    const connection = await amqp.connect('amqp://admin:admin123@localhost:5672');
    const channel = await connection.createChannel();

    // Ensure queue exists
    await channel.assertQueue('email.queue', { durable: true });

    // Test message
    const message = {
      notification_type: 'email',
      user_id: 'user-123',
      template_code: 'welcome_email',
      variables: {
        name: 'John Doe',
        email: 'john.doe@example.com'
      },
      request_id: 'test-' + Date.now()
    };

    console.log('📨 Sending message to email.queue:', JSON.stringify(message, null, 2));

    // Send message to queue
    channel.sendToQueue('email.queue', Buffer.from(JSON.stringify(message)), {
      persistent: true
    });

    console.log('✅ Message sent successfully!');
    console.log('📬 Check email service logs to see if message was processed');

    await channel.close();
    await connection.close();

  } catch (error) {
    console.error('❌ Error:', error);
  }
}

testCompleteWorkflow();