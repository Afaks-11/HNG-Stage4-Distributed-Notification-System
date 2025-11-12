import { Controller, Post, Body } from '@nestjs/common';
import { StatusService } from './status.service';
import { ok } from '../common/response';

@Controller('/api/v1')
export class StatusController {
  constructor(private readonly statusService: StatusService) {}

  @Post('/:notification_preference/status/')
  async update_status(@Body() body: any) {
    const { notification_id, status, error } = body;
    await this.statusService.add_status(notification_id, status, error);
    return ok({ notification_id, status }, 'status_updated');
  }
}
