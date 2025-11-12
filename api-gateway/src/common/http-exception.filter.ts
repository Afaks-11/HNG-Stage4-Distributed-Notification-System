import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
} from '@nestjs/common';

@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const res = ctx.getResponse();
    const status =
      exception instanceof HttpException
        ? exception.getStatus()
        : HttpStatus.INTERNAL_SERVER_ERROR;

    const message =
      exception instanceof HttpException ? exception.message : 'internal_error';

    res.status(status).json({
      success: false,
      error: message,
      message,
      meta: {
        total: 0,
        limit: 1,
        page: 1,
        total_pages: 0,
        has_next: false,
        has_previous: false,
      },
    });
  }
}
