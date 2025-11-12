import { Module } from '@nestjs/common';
import { NotificationsController } from './notifications.controller';
import { NotificationsService } from './notifications.service';
import { MqModule } from '../mq/mq.module';
import { RedisModule } from '../cache/redis.module';
import { StatusModule } from '../status/status.module';
import { AuthModule } from '../auth/auth.module';

@Module({
  imports: [MqModule, RedisModule, StatusModule, AuthModule],
  controllers: [NotificationsController],
  providers: [NotificationsService],
})
export class NotificationsModule {}
