import { Controller, Get } from '@nestjs/common';

@Controller('health')
export class HealthController {
  @Get()
  check() {
    return {
      success: true,
      message: 'Email Service is healthy',
      data: {
        service: 'email-service',
        status: 'up',
        timestamp: new Date().toISOString(),
      },
    };
  }
}
