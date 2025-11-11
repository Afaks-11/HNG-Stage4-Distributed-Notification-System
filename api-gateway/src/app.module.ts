import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config'
import { TypeOrmModule } from '@nestjs/typeorm';

import { HealthController } from './health/health.controller' 

import { StatusModule } from './status/status.module';
import { Notification } from './status/entities/notification.entity';
import { NotificationStatus } from './status/entities/notification_status.entity';

import { AppController } from './app.controller';
import { AppService } from './app.service';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    TypeOrmModule.forRootAsync({
      useFactory: () => ({
        type: 'postgres',
        url: process.env.STATUS_DB_URL,
        entities: [Notification, NotificationStatus],
        autoLoadEntities: true,
        synchronize: true
      })
    }),

    StatusModule
  ],
  controllers: [HealthController],
  providers: [AppService],
})
export class AppModule {}
