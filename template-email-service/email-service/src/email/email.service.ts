import { Injectable, Logger } from '@nestjs/common';
import axios from 'axios';
const nodemailer = require('nodemailer');

interface EmailMessage {
  user_id: string;
  template_code: string;
  variables: Record<string, any>;
  request_id: string;
  metadata?: Record<string, any>;
}

@Injectable()
export class EmailService {
  private readonly logger = new Logger(EmailService.name);
  private transporter: any;

  constructor() {
    this.initializeTransporter();
  }

  private initializeTransporter() {
    this.transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
      },
    });

    this.logger.log('📧 Email transporter initialized');
  }

  async sendEmail(message: EmailMessage): Promise<void> {
    try {
      // Step 1: Fetch template from Template Service
      const templateUrl = `${process.env.TEMPLATE_SERVICE_URL || 'http://localhost:3001'}/api/v1/templates/by-code/${message.template_code}`;
      
      this.logger.log(`📥 Fetching template: ${message.template_code}`);
      const templateResponse = await axios.get(templateUrl);
      const template = templateResponse.data.data;

      // Step 2: Render template with variables
      const subject = this.renderTemplate(template.subject, message.variables);
      const body = this.renderTemplate(template.body, message.variables);

      // Step 3: Get recipient email (from variables or metadata)
      const recipientEmail = message.variables.email || message.metadata?.email;
      
      if (!recipientEmail) {
        throw new Error('Recipient email not provided in variables or metadata');
      }

      // Step 4: Send email via SMTP
      const mailOptions = {
        from: process.env.EMAIL_USER,
        to: recipientEmail,
        subject: subject,
        html: body,
      };

      await this.transporter.sendMail(mailOptions);
      this.logger.log(`✅ Email sent to ${recipientEmail} (request: ${message.request_id})`);

    } catch (error) {
      this.logger.error(`❌ Failed to send email:`, error.message);
      throw error;
    }
  }

  private renderTemplate(template: string, variables: Record<string, any>): string {
    return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return variables[key] !== undefined ? String(variables[key]) : match;
    });
  }
}
