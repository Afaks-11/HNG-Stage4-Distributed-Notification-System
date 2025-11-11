import { Entity, Column, PrimaryGeneratedColumn, Index } from 'typeorm';
@Entity('notification_status')
export class NotificationStatus {
  @PrimaryGeneratedColumn('increment') id: string;
  @Index() @Column() notification_id: string;
  @Column() status: string;
  @Column({ nullable: true }) error?: string;
  @Column({ type: 'timestamptz' }) timestamp: Date;
  @Column({ type: 'int', default: 0 }) retry_count: number;
}
