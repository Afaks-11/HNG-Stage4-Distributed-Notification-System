import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, Index } from 'typeorm';

@Entity('templates')
export class Template {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  @Index()
  code: string;

  @Column()
  name: string;

  @Column()
  subject: string;

  @Column('text')
  body: string;

  @Column({ default: 'email' })
  type: string; // email, push, sms

  @Column({ default: 'en' })
  language: string;

  @Column({ default: 1 })
  version: number;

  @Column('jsonb', { nullable: true })
  variables: Record<string, any>;

  @Column('jsonb', { nullable: true })
  metadata: Record<string, any>;

  @Column({ default: true })
  is_active: boolean;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;
}

@Entity('template_versions')
export class TemplateVersion {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  @Index()
  template_id: string;

  @Column()
  version: number;

  @Column()
  subject: string;

  @Column('text')
  body: string;

  @Column('jsonb', { nullable: true })
  variables: Record<string, any>;

  @Column('jsonb', { nullable: true })
  metadata: Record<string, any>;

  @CreateDateColumn()
  created_at: Date;
}