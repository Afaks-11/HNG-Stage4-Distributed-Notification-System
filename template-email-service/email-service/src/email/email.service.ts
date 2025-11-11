import { Injectable, OnModuleInit, Logger } from '@nestjs/common';
import { EmailProvider } from './email.provider';
import { RedisService } from '../redis/redis.service';
import { CircuitBreakerService } from '../common/circuit-breaker.service';
import { StatusPublisherService } from '../status/status-publisher.service';
import { TemplateHelper } from './helpers/template.helper';
import axios from 'axios';

@Injectable()
export class EmailService implements OnModuleInit {
  private readonly logger = new Logger(EmailService.name);

  constructor(
    private readonly emailProvider: EmailProvider,
    private readonly redisService: RedisService,
    private readonly circuitBreakerService: CircuitBreakerService,
    private readonly statusPublisher: StatusPublisherService,
    private readonly templateHelper: TemplateHelper,
  ) {}

  onModuleInit() {
    this.circuitBreakerService.createBreaker(
      'template-service',
      async (templateCode: string) => {
        const url = `${process.env.TEMPLATE_SERVICE_URL || 'http://localhost:3001'}/api/v1/templates/by-code/${templateCode}`;
        const response = await axios.get(url, { timeout: 5000 });
        return response.data;
      },
      { timeout: 5000, resetTimeout: 30000 }
    );

    this.circuitBreakerService.createBreaker(
      'smtp',
      async (mailOptions: any) => {
        return await this.emailProvider.sendEmail(mailOptions);
      },
      { timeout: 15000, resetTimeout: 60000 }
    );
  }

  async processEmail(data: any) {
    const { message_id, template_code, recipient, subject, variables } = data;

    if (await this.redisService.isDuplicate(message_id)) {
      this.logger.warn(`⚠️  Duplicate message detected: ${message_id}`);
      return;
    }

    await this.statusPublisher.publishStatus(message_id, 'processing');

    try {
      let template = await this.redisService.getCachedTemplate(template_code);
      
      if (!template) {
        const templateBreaker = this.circuitBreakerService.getBreaker('template-service');
        const result = await templateBreaker.fire(template_code);
        template = result.data;
        await this.redisService.cacheTemplate(template_code, template);
      }

      const renderedBody = this.templateHelper.render(template.body, variables);
      const renderedSubject = subject || this.templateHelper.render(template.subject, variables);

      const smtpBreaker = this.circuitBreakerService.getBreaker('smtp');
      await smtpBreaker.fire({
        to: recipient,
        subject: renderedSubject,
        html: renderedBody,
      });

      await this.redisService.markAsProcessed(message_id);
      await this.statusPublisher.publishStatus(message_id, 'sent');
      
      this.logger.log(`✅ Email sent successfully to ${recipient}`);
    } catch (error) {
      await this.statusPublisher.publishStatus(message_id, 'failed', { error: error.message });
      throw error;
    }
  }
}
