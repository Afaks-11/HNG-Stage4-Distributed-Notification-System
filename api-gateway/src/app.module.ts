import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config'
import { TypeOrmModule } from '@nestjs/typeorm';

import { HealthController } from './health/health.controller' 
import { AppController } from './app.controller';

import { StatusModule } from './status/status.module';
import { MqModule } from './mq/mq.module';
import { AuthModule } from './auth/auth.module';
import { NotificationsModule } from './notifications/notifications.module';

import { AppService } from './app.service';

import { configSchema } from './config/config.validation';

import { Notification } from './status/entities/notification.entity';
import { NotificationStatus } from './status/entities/notification_status.entity';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, validationSchema: configSchema }),
    TypeOrmModule.forRootAsync({
      useFactory: () => ({
        type: 'postgres',
        url: process.env.STATUS_DB_URL,
        entities: [Notification, NotificationStatus],
        autoLoadEntities: true,
        synchronize: true,
      }),
    }),
    AuthModule,
    StatusModule,
    MqModule,
    NotificationsModule,
  ],
  controllers: [HealthController, AppController],
  providers: [AppService],
})
export class AppModule {}
