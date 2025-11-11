import { Injectable, Logger } from '@nestjs/common';
const nodemailer = require('nodemailer');

@Injectable()
export class EmailProvider {
  private transporter: any;
  private readonly logger = new Logger(EmailProvider.name);

  constructor() {
    this.transporter = nodemailer.createTransport({
      host: process.env.EMAIL_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.EMAIL_PORT || '587'),
      secure: process.env.EMAIL_SECURE === 'true',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
      },
    });
  }

  async sendEmail(mailOptions: { to: string; subject: string; html: string }) {
    const options = {
      from: process.env.EMAIL_USER,
      ...mailOptions,
    };

    try {
      const info = await this.transporter.sendMail(options);
      this.logger.log(`📧 Email sent: ${info.messageId}`);
      return info;
    } catch (error) {
      this.logger.error('❌ Email send failed:', error.message);
      throw error;
    }
  }
}
