from rest_framework.response import Response
from rest_framework import status
from typing import Optional, Dict, Any
from math import ceil


def create_response(
    success: bool = True,
    message: str = "",
    data: Optional[Any] = None,
    error: Optional[str] = None,
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict[str, Any]] = None
) -> Response:
    """
    Create a standardized API response
    
    Args:
        success: Whether the request was successful
        message: Response message
        data: Response data (optional)
        error: Error message (optional)
        status_code: HTTP status code
        meta: Pagination metadata (optional)
    
    Returns:
        Response: DRF Response object with standardized format
    """
    response_data = {
        "success": success,
        "message": message,
    }
    
    if data is not None:
        response_data["data"] = data
    
    if error:
        response_data["error"] = error
    
    if meta:
        response_data["meta"] = meta
    
    return Response(response_data, status=status_code)


def create_pagination_meta(
    total: int,
    limit: int,
    page: int
) -> Dict[str, Any]:
    """
    Create pagination metadata
    
    Args:
        total: Total number of items
        limit: Number of items per page
        page: Current page number (1-indexed)
    
    Returns:
        Dict containing pagination metadata
    """
    total_pages = ceil(total / limit) if limit > 0 else 0
    has_next = page < total_pages
    has_previous = page > 1
    
    return {
        "total": total,
        "limit": limit,
        "page": page,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_previous": has_previous,
    }

