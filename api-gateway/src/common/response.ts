export interface PaginationMeta {
  total: number;
  limit: number;
  page: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message: string;
  meta: PaginationMeta;
}
export function ok<T>(data: T, message = 'ok'): ApiResponse<T> {
  return {
    success: true,
    data,
    message,
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
export function fail(error: string, message = 'error'): ApiResponse {
  return {
    success: false,
    error,
    message,
    meta: {
      total: 0,
      limit: 1,
      page: 1,
      total_pages: 0,
      has_next: false,
      has_previous: false,
    },
  };
}
