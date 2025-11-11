import { Module } from '@nestjs/common';
import { EmailService } from './email.service';
import { EmailConsumer } from './email.consumer';
import { EmailProvider } from './email.provider';
import { CircuitBreakerService } from '../common/circuit-breaker.service';
import { StatusPublisherService } from '../status/status-publisher.service';
import { TemplateHelper } from './helpers/template.helper';
import { RabbitMQModule } from '../queue/rabbitmq.module';

@Module({
  imports: [RabbitMQModule],
  providers: [
    EmailService,
    EmailConsumer,
    EmailProvider,
    CircuitBreakerService,
    StatusPublisherService,
    TemplateHelper,
  ],
  exports: [EmailService],
})
export class EmailModule {}
