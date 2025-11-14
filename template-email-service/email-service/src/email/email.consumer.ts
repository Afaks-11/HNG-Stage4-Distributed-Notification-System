import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { EmailService } from './email.service';
import * as amqp from 'amqplib';

interface EmailMessage {
  notification_type: 'email';
  user_id: string;
  template_code: string;
  variables: Record<string, any>;
  request_id: string;
  priority?: number;
  metadata?: Record<string, any>;
}

@Injectable()
export class EmailConsumer implements OnModuleInit {
  private readonly logger = new Logger(EmailConsumer.name);
  private connection: any;
  private channel: any;

  constructor(private readonly emailService: EmailService) {}

  async onModuleInit() {
    await this.connectToRabbitMQ();
  }

  private async connectToRabbitMQ() {
    try {
      const rabbitmqUrl = process.env.RABBITMQ_URL || 'amqp://admin:admin123@localhost:5672';
      
      this.connection = await amqp.connect(rabbitmqUrl) as any;
      this.channel = await (this.connection as any).createChannel();

      await this.channel.assertQueue('email.queue', { durable: true });
      await this.channel.prefetch(1); // Process one message at a time

      this.logger.log('📬 Connected to RabbitMQ, listening for email messages...');

      this.channel.consume('email.queue', async (msg) => {
        if (msg) {
          await this.handleMessage(msg);
        }
      });

      this.connection.on('error', (err) => {
        this.logger.error('RabbitMQ connection error:', err);
      });

      this.connection.on('close', () => {
        this.logger.warn('RabbitMQ connection closed, reconnecting...');
        setTimeout(() => this.connectToRabbitMQ(), 5000);
      });

    } catch (error) {
      this.logger.error('Failed to connect to RabbitMQ:', error);
      setTimeout(() => this.connectToRabbitMQ(), 5000);
    }
  }

  private async handleMessage(msg: amqp.Message) {
    try {
      const message: EmailMessage = JSON.parse(msg.content.toString());
      this.logger.log(`📨 Processing email for user ${message.user_id}, template: ${message.template_code}`);

      // Send email
      await this.emailService.sendEmail(message);

      // Acknowledge message
      this.channel.ack(msg);
      this.logger.log(`✅ Email sent successfully for request ${message.request_id}`);

    } catch (error) {
      this.logger.error(`❌ Error processing message:`, error);
      
      // Reject and requeue message (up to 3 retries)
      const retryCount = (msg.properties.headers['x-retry-count'] || 0) + 1;
      
      if (retryCount < 3) {
        this.logger.warn(`🔄 Retrying message (attempt ${retryCount}/3)`);
        this.channel.nack(msg, false, true);
      } else {
        this.logger.error(`💀 Message failed after 3 attempts, sending to DLQ`);
        this.channel.nack(msg, false, false); // Don't requeue
      }
    }
  }
}
