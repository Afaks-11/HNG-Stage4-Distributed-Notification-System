import {
  Controller,
  Post,
  Get,
  Body,
  Param,
  UseGuards,
  Req,
} from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt.guard';
import { NotificationsService } from './notifications.service';
import { CreateNotificationDto } from './dto/create_notification.dto';
import { ok, fail } from '../common/response';
import { StatusService } from 'src/status/status.service';

@Controller('/api/v1/notifications')
export class NotificationsController {
  constructor(
    private readonly service: NotificationsService,
    private readonly status: StatusService,
  ) {}
  @UseGuards(JwtAuthGuard)
  @Post('/')
  async create(@Body() body: CreateNotificationDto, @Req() req: any) {
    try {
      const result = await this.service.create(body, req.user);
      return ok(result, 'notification_enqueued');
    } catch (e) {
      return fail(e.message ?? 'unable_to_enqueue', 'enqueue_failed');
    }
  }

  @UseGuards(JwtAuthGuard)
  @Get('/:id/status')
  async getStatus(@Param('id') id: string) {
    const latest = await this.status.get_latest_status(id);

    if (!latest || latest.length === 0) {
      return fail('notification_not_found', 'not_found');
    }

    return ok(
      {
        notification_id: id,
        latest_status: latest[0].status,
        updated_at: latest[0].timestamp,
      },
      'notification_status_retrieved',
    );
  }
}
