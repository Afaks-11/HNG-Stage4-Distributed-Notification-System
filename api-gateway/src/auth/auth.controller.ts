import { Controller, Post, Body, Get, UseGuards, Req } from '@nestjs/common';
import { AuthService } from './auth.service';
import { JwtAuthGuard } from './jwt.guard';

@Controller('/api/v1/auth')
export class AuthController {
  constructor(private readonly auth: AuthService) {}

  @Post('/register')
  async register(@Body() body: { email: string; password: string }) {
    const user = await this.auth.register(body.email, body.password);
    return {
      success: true,
      message: 'registered',
      data: user,
      meta: {
        total: 1,
        limit: 1,
        page: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    };
  }

  @Post('/login')
  async login(@Body() body: { email: string; password: string }) {
    const res = await this.auth.login(body.email, body.password);
    return {
      success: true,
      message: 'logged_in',
      data: res,
      meta: {
        total: 1,
        limit: 1,
        page: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    };
  }

  @UseGuards(JwtAuthGuard)
  @Get('/test')
  async test(@Req() req: any) {
    return {
      success: true,
      message: 'JWT authentication works',
      data: { user: req.user },
      meta: {
        total: 1,
        limit: 1,
        page: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    };
  }
}
