import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity('templates')
export class Template {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  code: string; // e.g., 'welcome_email', 'reset_password'

  @Column()
  name: string; // Human-readable name

  @Column()
  subject: string; // Email subject with {{variables}}

  @Column('text')
  body: string; // Email body HTML with {{variables}}

  @Column({ default: true })
  is_active: boolean; // Can be disabled without deleting

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;
}
