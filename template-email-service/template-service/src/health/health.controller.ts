import { Controller, Get } from '@nestjs/common';
import { InjectDataSource } from '@nestjs/typeorm';
import { DataSource } from 'typeorm';

@Controller('health')
export class HealthController {
  constructor(@InjectDataSource() private dataSource: DataSource) {}

  @Get()
  async check() {
    const isDbConnected = this.dataSource.isInitialized;

    return {
      success: isDbConnected,
      message: isDbConnected ? 'Template Service is healthy' : 'Template Service has issues',
      data: {
        service: 'template-service',
        status: isDbConnected ? 'up' : 'degraded',
        timestamp: new Date().toISOString(),
        database: {
          status: isDbConnected ? 'connected' : 'disconnected',
        },
      },
    };
  }
}
