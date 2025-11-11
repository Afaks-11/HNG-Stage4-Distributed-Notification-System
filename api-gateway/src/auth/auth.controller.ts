import { Controller, Get, UseGuards, Req } from '@nestjs/common';
import { JwtAuthGuard } from './jwt.gaurd';

@Controller('/protected')
export class AuthController {
  @UseGuards(JwtAuthGuard)
  @Get('/test')
  async test(@Req() req: { user: string }) {
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
