import { Injectable, Inject, Logger } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';

@Injectable()
export class StatusPublisherService {
  private readonly logger = new Logger(StatusPublisherService.name);

  constructor(
    @Inject('RABBITMQ_SERVICE') private readonly client: ClientProxy,
  ) {}

  async publishStatus(messageId: string, status: string, metadata?: any) {
    try {
      await this.client.emit('notification.status.queue', {
        message_id: messageId,
        status,
        timestamp: new Date().toISOString(),
        ...metadata,
      }).toPromise();
      this.logger.log(`📤 Status published: ${messageId} - ${status}`);
    } catch (error) {
      this.logger.error('Failed to publish status:', error.message);
    }
  }
}
