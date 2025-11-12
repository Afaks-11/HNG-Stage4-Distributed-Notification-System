import {
  Injectable,
  OnModuleInit,
  OnModuleDestroy,
  Logger,
} from '@nestjs/common';
import * as amqplib from 'amqplib';

@Injectable()
export class MqService implements OnModuleInit, OnModuleDestroy {
  private conn: amqplib.Connection;
  private channel: amqplib.Channel;
  readonly exchange = 'notifications.direct';
  private readonly logger = new Logger(MqService.name);

  async onModuleInit() {
    let retries = 5;
    while (retries > 0) {
      try {
        this.logger.log(
          `Connecting to RabbitMQ at ${process.env.RABBITMQ_URL}...`,
        );
        this.conn = await amqplib.connect(process.env.RABBITMQ_URL);
        this.channel = await this.conn.createChannel();

        await this.channel.assertExchange(this.exchange, 'direct', {
          durable: true,
        });
        await this.channel.assertExchange('notifications.failed', 'direct', {
          durable: true,
        });

        await this.channel.assertQueue('email.queue', {
          durable: true,
          arguments: {
            'x-dead-letter-exchange': 'notifications.failed',
            'x-dead-letter-routing-key': 'email_failed',
          },
        });
        await this.channel.assertQueue('push.queue', {
          durable: true,
          arguments: {
            'x-dead-letter-exchange': 'notifications.failed',
            'x-dead-letter-routing-key': 'push_failed',
          },
        });
        await this.channel.assertQueue('failed.queue', { durable: true });

        await this.channel.bindQueue('email.queue', this.exchange, 'email');
        await this.channel.bindQueue('push.queue', this.exchange, 'push');
        await this.channel.bindQueue(
          'failed.queue',
          'notifications.failed',
          'email_failed',
        );
        await this.channel.bindQueue(
          'failed.queue',
          'notifications.failed',
          'push_failed',
        );

        this.logger.log('RabbitMQ connection established successfully');
        return;
      } catch (err) {
        this.logger.error(`RabbitMQ connection failed: ${err.message}`);
        retries--;
        if (retries === 0) {
          throw new Error('RabbitMQ not available after retries');
        }
        this.logger.warn(`Retrying in 5s... (${retries} retries left)`);
        await new Promise((res) => setTimeout(res, 5000));
      }
    }
  }

  async publish(
    routing_key: 'email' | 'push',
    payload: any,
    headers: Record<string, any>,
  ) {
    if (!this.channel) {
      throw new Error('RabbitMQ channel not initialized');
    }
    const body = Buffer.from(JSON.stringify(payload));
    this.channel.publish(this.exchange, routing_key, body, {
      contentType: 'application/json',
      correlationId: payload.correlation_id,
      messageId: payload.notification_id,
      headers,
      persistent: true,
    });
  }

  async onModuleDestroy() {
    await this.channel?.close();
    await this.conn?.close();
  }
}
