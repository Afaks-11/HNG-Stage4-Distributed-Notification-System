import { IsEnum, IsString, IsInt, IsOptional, IsObject } from 'class-validator';

export enum NotificationType {
  email = 'email',
  push = 'push',
}

export class CreateNotificationDto {
  @IsEnum(NotificationType)
  notification_type: NotificationType;

  @IsString()
  template_code: string;

  @IsObject()
  variables: Record<string, any>;

  @IsString()
  request_id: string;

  @IsInt()
  priority: number;

  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}
