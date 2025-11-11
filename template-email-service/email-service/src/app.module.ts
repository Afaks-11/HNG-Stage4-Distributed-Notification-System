import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { EmailModule } from './email/email.module';
import { RedisModule } from './redis/redis.module';
import { RabbitMQModule } from './queue/rabbitmq.module';
import { HealthController } from './health.controller';
import { CircuitBreakerService } from './common/circuit-breaker.service';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    RedisModule,
    RabbitMQModule,
    EmailModule,
  ],
  controllers: [HealthController],
  providers: [CircuitBreakerService],
})
export class AppModule {}
