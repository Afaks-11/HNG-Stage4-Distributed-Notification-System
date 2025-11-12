import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Notification } from './entities/notification.entity';
import { NotificationStatus } from './entities/notification_status.entity';

@Injectable()
export class StatusService {
  constructor(
    @InjectRepository(Notification) private notifRepo: Repository<Notification>,
    @InjectRepository(NotificationStatus)
    private statusRepo: Repository<NotificationStatus>,
  ) {}

  async get_latest_notification(notificationId: string) {
    return await this.notifRepo.find({
      where: { id: notificationId }, // use id, not notification_id
      order: { created_at: 'DESC' },
      take: 1,
    });
  }

  async create_pending(notification: Notification) {
    await this.notifRepo.save(notification);
    await this.statusRepo.save({
      notification_id: notification.id,
      status: 'pending',
      timestamp: new Date(),
      retry_count: 0,
    });
  }

  async add_status(
    notification_id: string,
    status: 'delivered' | 'failed',
    error?: string,
  ) {
    await this.statusRepo.save({
      notification_id,
      status,
      error: error ?? undefined,
      timestamp: new Date(),
      retry_count: status === 'failed' ? 1 : 0,
    });
  }

  async get_latest_status(notificationId: string) {
    return this.statusRepo.find({
      where: { notification_id: notificationId },
      order: { timestamp: 'DESC' },
      take: 1,
    });
  }
}
