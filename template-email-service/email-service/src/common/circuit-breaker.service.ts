import { Injectable, Logger } from '@nestjs/common';
import CircuitBreaker from 'opossum';

@Injectable()
export class CircuitBreakerService {
  private breakers = new Map<string, CircuitBreaker>();
  private readonly logger = new Logger(CircuitBreakerService.name);

  createBreaker(name: string, action: (...args: any[]) => Promise<any>, options?: any): CircuitBreaker {
    const breaker = new CircuitBreaker(action, {
      timeout: options?.timeout || 10000,
      errorThresholdPercentage: options?.errorThresholdPercentage || 50,
      resetTimeout: options?.resetTimeout || 60000,
      rollingCountTimeout: options?.rollingCountTimeout || 30000,
      ...options,
    });

    breaker.on('open', () => this.logger.warn(`⚠️  Circuit breaker "${name}" opened`));
    breaker.on('close', () => this.logger.log(`✅ Circuit breaker "${name}" closed`));
    breaker.on('halfOpen', () => this.logger.log(`🔄 Circuit breaker "${name}" half-open`));
    breaker.on('failure', (error) => this.logger.error(`❌ Circuit breaker "${name}" failure:`, error.message));

    this.breakers.set(name, breaker);
    return breaker;
  }

  getBreaker(name: string): CircuitBreaker | undefined {
    return this.breakers.get(name);
  }
}
