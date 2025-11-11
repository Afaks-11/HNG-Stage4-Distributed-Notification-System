import { Controller, Logger } from '@nestjs/common';
import { MessagePattern, Ctx, Payload, RmqContext } from '@nestjs/microservices';
import { EmailService } from './email.service';

@Controller()
export class EmailConsumer {
  private readonly logger = new Logger(EmailConsumer.name);
  private readonly MAX_RETRIES = 3;

  constructor(private readonly emailService: EmailService) {}

  @MessagePattern('email.queue')
  async handleEmailMessage(@Payload() data: any, @Ctx() context: RmqContext) {
    const channel = context.getChannelRef();
    const originalMsg = context.getMessage();
    
    const retryCount = (originalMsg.properties.headers['x-retry-count'] || 0);
    
    this.logger.log(`📧 Processing email message (attempt ${retryCount + 1})`);

    try {
      await this.emailService.processEmail(data);
      channel.ack(originalMsg);
      this.logger.log('✅ Email processed successfully');
    } catch (error) {
      this.logger.error('❌ Email processing failed:', error.message);

      if (retryCount < this.MAX_RETRIES) {
        const delay = Math.pow(2, retryCount) * 1000;
        this.logger.log(`🔄 Scheduling retry in ${delay}ms`);
        
        setTimeout(() => {
          channel.nack(originalMsg, false, true);
        }, delay);
      } else {
        this.logger.error('💀 Max retries exceeded, sending to DLQ');
        channel.nack(originalMsg, false, false);
      }
    }
  }
}
