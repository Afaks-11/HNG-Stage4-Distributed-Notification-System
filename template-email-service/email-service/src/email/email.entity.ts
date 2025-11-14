import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, Index } from 'typeorm';

export enum NotificationStatus {
  PENDING = 'pending',
  DELIVERED = 'delivered',
  FAILED = 'failed'
}

@Entity('email_notifications')
export class EmailNotification {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  @Index()
  notification_id: string;

  @Column()
  @Index()
  user_id: string;

  @Column()
  template_code: string;

  @Column('jsonb', { nullable: true })
  variables: Record<string, any>;

  @Column()
  @Index()
  request_id: string;

  @Column({ default: 1 })
  priority: number;

  @Column('jsonb', { nullable: true })
  metadata: Record<string, any>;

  // Email specific fields
  @Column()
  to_email: string;

  @Column({ nullable: true })
  from_email: string;

  @Column()
  subject: string;

  @Column('text')
  body: string;

  @Column({ nullable: true })
  html_body: string;

  // Status tracking
  @Column({
    type: 'enum',
    enum: NotificationStatus,
    default: NotificationStatus.PENDING
  })
  status: NotificationStatus;

  @Column({ nullable: true })
  sent_at: Date;

  @Column({ nullable: true })
  delivered_at: Date;

  @Column({ nullable: true })
  failed_at: Date;

  @Column('text', { nullable: true })
  error_message: string;

  @Column({ default: 0 })
  retry_count: number;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;
}

@Entity('email_notification_logs')
export class EmailNotificationLog {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  @Index()
  notification_id: string;

  @Column()
  status: string;

  @CreateDateColumn()
  timestamp: Date;

  @Column('text', { nullable: true })
  error_message: string;

  @Column('jsonb', { nullable: true })
  metadata: Record<string, any>;
}