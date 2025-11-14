export interface PaginationMeta {
  total: number;
  limit: number;
  page: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message: string;
  meta?: PaginationMeta;
}

export function createResponse<T>(
  success: boolean,
  message: string,
  data?: T,
  error?: string,
  meta?: PaginationMeta
): ApiResponse<T> {
  const response: ApiResponse<T> = {
    success,
    message,
  };

  if (data !== undefined) {
    response.data = data;
  }

  if (error) {
    response.error = error;
  }

  if (meta) {
    response.meta = meta;
  }

  return response;
}

export function createPaginationMeta(
  total: number,
  limit: number,
  page: number
): PaginationMeta {
  const total_pages = Math.ceil(total / limit);
  
  return {
    total,
    limit,
    page,
    total_pages,
    has_next: page < total_pages,
    has_previous: page > 1,
  };
}