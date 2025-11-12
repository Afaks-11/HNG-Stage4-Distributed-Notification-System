import { Module, Global } from '@nestjs/common';
import { MqService } from './mq.service';
import { MqController } from './mq.controller';
@Global()
@Module({
  providers: [MqService],
  exports: [MqService],
  controllers: [MqController],
})
export class MqModule {}
