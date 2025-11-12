import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import Redis from 'ioredis';

@Injectable()
export class RedisService implements OnModuleInit, OnModuleDestroy {
  private client: Redis;
  async onModuleInit() {
    this.client = new Redis(process.env.REDIS_URL!);
  }
  async set_idempotency(
    request_id: string,
    notification_id: string,
    ttl_seconds = 86400,
  ) {
    return this.client.set(
      `idempotency:${request_id}`,
      notification_id,
      'EX',
      ttl_seconds,
      'NX',
    );
  }
  async get_idempotency(request_id: string) {
    return this.client.get(`idempotency:${request_id}`);
  }
  async onModuleDestroy() {
    await this.client?.quit();
  }
}
