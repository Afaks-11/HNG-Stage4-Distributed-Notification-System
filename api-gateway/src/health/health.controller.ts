import { Controller, Get } from '@nestjs/common'
import { uptime } from 'process';

@Controller('/health')
export class HealthController {
  @Get()
  health() {
    return {
      status: 'ok',
      dependencies: { mq: 'unknown', db: 'configured', cache: 'unknown' },
      uptime_ms: Math.floor(process.uptime() * 1000),
    };
  }
}