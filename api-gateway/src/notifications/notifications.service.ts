import { Injectable, Logger } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import { MqService } from '../mq/mq.service';
import { RedisService } from '../cache/redis.service';
import { StatusService } from '../status/status.service';
import { Notification } from '../status/entities/notification.entity';
import { CreateNotificationDto } from './dto/create_notification.dto';

@Injectable()
export class NotificationsService {
  private readonly logger = new Logger(NotificationsService.name);

  constructor(
    private readonly mq: MqService,
    private readonly redis: RedisService,
    private readonly status: StatusService,
  ) {}

  async create(dto: CreateNotificationDto, auth_user: { userId: string }) {
    this.logger.debug(`Incoming DTO: ${JSON.stringify(dto)}`);
    this.logger.debug(`Auth user: ${JSON.stringify(auth_user)}`);

    const existing = await this.redis.get_idempotency(dto.request_id);
    if (existing) {
      const latest = await this.status.get_latest_status(existing);
      return {
        notification_id: existing,
        latest_status: latest[0]?.status ?? 'pending',
        idempotent: true,
      };
    }

    const notification_id = `notif_${uuidv4()}`;
    const correlation_id = `corr_${uuidv4()}`;

    const record: Notification = {
      id: notification_id,
      user_id: auth_user.userId,
      type: dto.notification_type,
      template_code: dto.template_code,
      request_id: dto.request_id,
      correlation_id,
      priority: dto.priority,
      created_at: new Date(),
    };

    try {
      await this.status.create_pending(record);
    } catch (e) {
      this.logger.error(`DB insert failed: ${e.message}`, e.stack);
      throw e;
    }

    const message = {
      ...record,
      request_id: dto.request_id,
      notification_type: dto.notification_type,
      correlation_id,
      variables: dto.variables,
    };
    await this.redis.set_idempotency(dto.request_id, notification_id);
    await this.mq.publish(dto.notification_type, message, {
      x_trace_id: correlation_id,
    });
    this.logger.debug(`Using userId: ${auth_user.userId}`);

    this.logger.debug(`Notification created: ${notification_id}`);
    return { notification_id, latest_status: 'pending', idempotent: false };
  }
}
