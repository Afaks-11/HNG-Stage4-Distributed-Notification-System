import { Controller, Post, Body } from '@nestjs/common';

@Controller('/api/v1')
export class StatusController {
  constructor() {}
  @Post('/:notification_preference/status/')
  async update_status(@Body() body: any) {
    return { success: true, message: 'status_endpoint_placeholder', meta: { total: 0, limit: 1, page: 1, total_pages: 0, has_next: false, has_previous: false } };
  }
}
