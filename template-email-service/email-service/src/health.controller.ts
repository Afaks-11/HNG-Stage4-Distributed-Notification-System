import { Controller, Get } from '@nestjs/common';
import { RedisService } from './redis/redis.service';
import { CircuitBreakerService } from './common/circuit-breaker.service';

@Controller('health')
export class HealthController {
  constructor(
    private readonly redisService: RedisService,
    private readonly circuitBreakerService: CircuitBreakerService,
  ) {}

  @Get()
  async check() {
    const redisHealthy = this.redisService.isConnected;
    const smtpBreaker = this.circuitBreakerService.getBreaker('smtp');
    const templateBreaker = this.circuitBreakerService.getBreaker('template-service');

    const isHealthy = true; // Service runs even without Redis

    return {
      success: isHealthy,
      message: isHealthy ? 'Email Service is healthy' : 'Email Service has issues',
      data: {
        service: 'email-service',
        status: isHealthy ? 'up' : 'degraded',
        timestamp: new Date().toISOString(),
        components: {
          redis: {
            status: redisHealthy ? 'connected' : 'disconnected',
            note: redisHealthy ? undefined : 'Optional - Service runs without caching',
          },
          smtp: smtpBreaker ? {
            status: smtpBreaker.opened ? 'open' : 'closed',
            circuit_breaker: {
              state: smtpBreaker.opened ? 'open' : 'closed',
              stats: smtpBreaker.stats,
            },
          } : {
            status: 'not_initialized',
            note: 'Circuit breaker will be created on first email send',
          },
          template_service: templateBreaker ? {
            status: templateBreaker.opened ? 'open' : 'closed',
            circuit_breaker: {
              state: templateBreaker.opened ? 'open' : 'closed',
              stats: templateBreaker.stats,
            },
          } : {
            status: 'not_initialized',
            note: 'Circuit breaker will be created on first template fetch',
          },
        },
      },
    };
  }
}
