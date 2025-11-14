import { Controller, Get, Post, Body, Param, HttpException, HttpStatus } from '@nestjs/common';
import axios from 'axios';

@Controller()
export class AppController {
  
  @Get('health')
  health() {
    return { success: true, message: 'API Gateway is running', data: null, error: null };
  }

  // Auth routes
  @Post('auth/register')
  async register(@Body() body: any) {
    try {
      const response = await axios.post('http://auth-service:8000/auth/register/', body);
      return response.data;
    } catch (error) {
      throw new HttpException(error.response?.data || 'Auth service error', error.response?.status || 500);
    }
  }

  @Post('auth/login')
  async login(@Body() body: any) {
    try {
      const response = await axios.post('http://auth-service:8000/auth/login/', body);
      return response.data;
    } catch (error) {
      throw new HttpException(error.response?.data || 'Auth service error', error.response?.status || 500);
    }
  }

  // User routes
  @Get('users/:id/preferences')
  async getUserPreferences(@Param('id') id: string) {
    try {
      const response = await axios.get(`http://user-service:8001/api/v1/users/${id}/preferences/`);
      return response.data;
    } catch (error) {
      throw new HttpException(error.response?.data || 'User service error', error.response?.status || 500);
    }
  }

  // Template routes
  @Post('templates')
  async createTemplate(@Body() body: any) {
    try {
      const response = await axios.post('http://template-service:3001/api/v1/templates', body);
      return response.data;
    } catch (error) {
      throw new HttpException(error.response?.data || 'Template service error', error.response?.status || 500);
    }
  }

  @Get('templates/by-code/:code')
  async getTemplate(@Param('code') code: string) {
    try {
      const response = await axios.get(`http://template-service:3001/api/v1/templates/by-code/${code}`);
      return response.data;
    } catch (error) {
      throw new HttpException(error.response?.data || 'Template service error', error.response?.status || 500);
    }
  }

  // Notification routes
  @Post('notifications/send')
  async sendNotification(@Body() body: any) {
    try {
      const { user_id, template_code, variables } = body;
      
      // Get user preferences
      const userResponse = await axios.get(`http://user-service:8001/api/v1/users/${user_id}/preferences/`);
      const preferences = userResponse.data.data;

      const results: any[] = [];

      // Send email if enabled
      if (preferences.email_notifications) {
        try {
          const emailResponse = await axios.post('http://email-service:3002/api/v1/email/send', {
            template_code,
            variables: { ...variables, email: preferences.email },
            request_id: `req-${Date.now()}`
          });
          results.push({ type: 'email', success: true, data: emailResponse.data });
        } catch (error) {
          results.push({ type: 'email', success: false, error: error.message });
        }
      }

      // Send push if enabled
      if (preferences.push_notifications) {
        try {
          const pushResponse = await axios.post('http://push-service:8003/api/v1/push/send', {
            user_id,
            template_code,
            variables
          });
          results.push({ type: 'push', success: true, data: pushResponse.data });
        } catch (error) {
          results.push({ type: 'push', success: false, error: error.message });
        }
      }

      return {
        success: true,
        message: 'Notification processing completed',
        data: { results },
        error: null
      };
    } catch (error) {
      throw new HttpException(error.response?.data || 'Notification service error', error.response?.status || 500);
    }
  }
}