import { Controller, Get } from '@nestjs/common';
import { MqService } from './mq.service';

@Controller('/mq')
export class MqController {
  constructor(private readonly mq: MqService) {}

  @Get('/test')
  async test() {
    await this.mq.publish(
      'email',
      { notification_id: 'test', correlation_id: 'corr1' },
      {},
    );
    return { success: true };
  }
}
