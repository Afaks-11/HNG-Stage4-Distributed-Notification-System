import { Injectable, OnModuleInit, Logger } from '@nestjs/common';
import { createClient, RedisClientType } from 'redis';

@Injectable()
export class RedisService implements OnModuleInit {
  private client: RedisClientType;
  private readonly logger = new Logger(RedisService.name);
  public isConnected = false;

  async onModuleInit() {
    this.client = createClient({
      socket: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        connectTimeout: 5000,
        reconnectStrategy: false,
      },
    });

    this.client.on('error', (err) => {
      this.isConnected = false;
      this.logger.warn('⚠️ Redis not available: ', err.message);
    });

    this.client.on('connect', () => {
      this.isConnected = true;
      this.logger.log('✅ Connected to Redis');
    });

    try {
      await this.client.connect();
      this.logger.log('✅ Redis connection established');
    } catch (error) {
      this.logger.warn('⚠️ Redis not available - Service will run without caching: ', error.message);
    }
  }

  async isDuplicate(messageId: string): Promise<boolean> {
    if (!this.isConnected) return false;
    try {
      const key = `processed:${messageId}`;
      const exists = await this.client.exists(key);
      return exists === 1;
    } catch (error) {
      this.logger.warn('Redis check failed, allowing message:', error.message);
      return false;
    }
  }

  async markAsProcessed(messageId: string): Promise<void> {
    if (!this.isConnected) return;
    try {
      const key = `processed:${messageId}`;
      await this.client.setEx(key, 86400, 'processed'); // 24 hours TTL
    } catch (error) {
      this.logger.warn('Redis mark failed:', error.message);
    }
  }

  async getCachedTemplate(templateCode: string): Promise<any> {
    if (!this.isConnected) return null;
    try {
      const key = `template:${templateCode}`;
      const cached = await this.client.get(key);
      return cached ? JSON.parse(cached as string) : null;
    } catch (error) {
      this.logger.warn('Redis get failed:', error.message);
      return null;
    }
  }

  async cacheTemplate(templateCode: string, template: any): Promise<void> {
    if (!this.isConnected) return;
    try {
      const key = `template:${templateCode}`;
      await this.client.setEx(key, 3600, JSON.stringify(template)); // 1 hour TTL
    } catch (error) {
      this.logger.warn('Redis cache failed:', error.message);
    }
  }
}
