import { Entity, Column, PrimaryColumn } from 'typeorm';
@Entity('notifications')
export class Notification {
  @PrimaryColumn() id: string;
  @Column() user_id: string;
  @Column() type: string;
  @Column() template_code: string;
  @Column() request_id: string;
  @Column() correlation_id: string;
  @Column({ type: 'int' }) priority: number;
  @Column({ type: 'timestamptz' }) created_at: Date;
}
