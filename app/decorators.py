import time
from functools import wraps
from typing import Callable

import requests
from fastapi import HTTPException, status

from app.auth.token_repository import get_last_token

# According to QuickBooks API guidelines, the rate limit is 5 requests per second.
RATE_LIMIT_MAX_RETRIES = 5
# According to QuickBooks API guidelines, the initial delay is 60 seconds.
RATE_LIMIT_DEFAULT_DELAY = 60.0

def handle_rate_limit(max_retries: int = RATE_LIMIT_MAX_RETRIES,
                     delay: float = RATE_LIMIT_DEFAULT_DELAY):
    """Decorator to handle rate limiting with fixed delay per QuickBooks API guidelines."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code != status.HTTP_429_TOO_MANY_REQUESTS:
                        raise
                    time.sleep(delay)
                    
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded after multiple retries"
            )
        return wrapper
    return decorator

def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except HTTPException:
            # Let FastAPI handle HTTPException as is
            raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == status.HTTP_401_UNAUTHORIZED:
                # Token is invalid or expired, refresh it
                token = get_last_token()
                self.auth_service.refresh_token(token)
                new_token = get_last_token()
                # retry the function with the new token
                return func(self, *args, **kwargs)
            elif e.response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                # Rate limit error - will be handled by the decorator
                raise
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"QuickBooks API error: {str(e)}"
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service unavailable: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
    return wrapper

def require_token(func: Callable) -> Callable:
    """Decorator to for an API which requires a token."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            token = get_last_token()
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No token found. Authenticate first."
                )
            if token.is_expired():
                self.auth_service.refresh_token(token)
                new_token = get_last_token()
                return func(self, *args, **kwargs)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def quickbooks_api_wrapper(func: Callable) -> Callable:
    """Wrapper to handle rate limiting, errors, and token requirements for QuickBooks API calls."""
    return handle_rate_limit()(handle_errors(require_token(func)(func)))

def auth_endpoint_wrapper(func: Callable) -> Callable:
    """Decorator to handle authentication-related errors."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication request failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
    return wrapper