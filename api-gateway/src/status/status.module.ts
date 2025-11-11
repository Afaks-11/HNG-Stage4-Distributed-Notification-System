import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { StatusService } from './status.service'
import { StatusController } from './status.controller';
import { Notification } from './entities/notification.entity';
import { NotificationStatus } from './entities/notification_status.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Notification, NotificationStatus])],
  providers: [StatusService],
  controllers: [StatusController],
  exports: [StatusService],
})
export class StatusModule {}
