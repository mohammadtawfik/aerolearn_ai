# /app/core/api/api_client.py

import abc
import time
import threading
from typing import Any, Callable, Dict, Optional, Tuple
from functools import wraps

class APIClientError(Exception):
    """Base exception for API client errors."""
    pass

class RateLimitExceeded(APIClientError):
    """Raised when API rate limits are exceeded."""
    pass

class APIClient(metaclass=abc.ABCMeta):
    """
    Abstract base API client.
    Provides error handling, rate limiting, basic request/response interface, and caching hooks.
    Extend this class for each 3rd-party API client.
    """

    # For demonstration, a simple in-memory cache
    _cache: Dict[Tuple[str, str], Tuple[Any, float]] = {}
    _cache_lock = threading.Lock()
    _rate_limit: int = 5  # requests per period
    _rate_period: int = 1  # period in seconds
    _call_times = []
    _call_times_lock = threading.Lock()

    def __init__(self, cache_ttl: Optional[int] = None):
        self.cache_ttl = cache_ttl or 60  # cache time-to-live in seconds

    @abc.abstractmethod
    def authenticate(self):
        """Authenticate with the API. To be implemented by subclass."""
        raise NotImplementedError

    def rate_limited(self, func: Callable) -> Callable:
        """Decorator for rate limiting."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self._call_times_lock:
                now = time.time()
                # Remove expired timestamps
                self._call_times = [t for t in self._call_times if now - t < self._rate_period]
                if len(self._call_times) >= self._rate_limit:
                    raise RateLimitExceeded(f"Exceeded {self._rate_limit} requests per {self._rate_period} seconds")
                self._call_times.append(now)
            return func(*args, **kwargs)
        return wrapper

    def get_cache(self, key: Tuple[str, str]) -> Optional[Any]:
        with self._cache_lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            value, expiry = entry
            if time.time() > expiry:
                del self._cache[key]
                return None
            return value

    def set_cache(self, key: Tuple[str, str], value: Any):
        with self._cache_lock:
            self._cache[key] = (value, time.time() + self.cache_ttl)

    def request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Core request handler; subclasses should override or call super().
        Handles rate limiting, caching (by method+endpoint), and error propagation.
        """
        cache_key = (method, endpoint)
        cached = self.get_cache(cache_key)
        if cached is not None:
            return cached
        # Apply rate limiting
        rate_limited_request = self.rate_limited(self._do_request)
        result = rate_limited_request(method, endpoint, **kwargs)
        self.set_cache(cache_key, result)
        return result

    @abc.abstractmethod
    def _do_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Performs the actual API request. Subclasses should implement this.
        """
        raise NotImplementedError

    def clear_cache(self):
        with self._cache_lock:
            self._cache.clear()


# /app/core/api/deepseek_client.py

from .api_client import APIClient, APIClientError

class DeepSeekAPIError(APIClientError):
    pass

class DeepSeekClient(APIClient):
    """
    Concrete API client for DeepSeek services.
    """

    def __init__(self, api_key: str, endpoint_base: str = "https://api.deepseek.com/v1/", cache_ttl: int = 60):
        super().__init__(cache_ttl=cache_ttl)
        self.api_key = api_key
        self.endpoint_base = endpoint_base
        self.token = None

    def authenticate(self):
        """
        Authenticate with DeepSeek. In practice, store the API key or exchange for short-lived token.
        """
        self.token = self.api_key  # Simulate token, could expand to re-auth flow

    def _do_request(self, method: str, endpoint: str, **kwargs):
        """
        Implement actual HTTP request logic here (use requests, httpx, etc.).
        This is a stub for demonstration.
        """
        # Example: headers, simulated network call and error handling
        if self.token is None:
            self.authenticate()
        url = self.endpoint_base + endpoint
        headers = {"Authorization": f"Bearer {self.token}"}

        # Simulated network request
        print(f"[DeepSeek] {method} {url} headers={headers} kwargs={kwargs}")
        if "fail" in kwargs:
            raise DeepSeekAPIError("Simulated DeepSeek API failure")
        return {"status": "success", "url": url, "method": method, "params": kwargs, "service": "DeepSeek"}


# /app/core/api/google_drive_client.py

from .api_client import APIClient, APIClientError

class GoogleDriveAPIError(APIClientError):
    pass

class GoogleDriveClient(APIClient):
    """
    Concrete API client for Google Drive services.
    """

    def __init__(self, credentials: dict, endpoint_base: str = "https://www.googleapis.com/drive/v3/", cache_ttl: int = 60):
        super().__init__(cache_ttl=cache_ttl)
        self.credentials = credentials
        self.endpoint_base = endpoint_base
        self.token = None

    def authenticate(self):
        """
        Authenticate with Google Drive API.
        This method should handle OAuth2 flow or service account logic as appropriate.
        """
        # For demonstration, pretend that the credentials dict contains a token.
        self.token = self.credentials.get("access_token", "dummy-access-token")

    def _do_request(self, method: str, endpoint: str, **kwargs):
        """
        Implement actual HTTP request logic here (use requests, google-auth, etc.).
        This is a stub for demonstration.
        """
        if self.token is None:
            self.authenticate()
        url = self.endpoint_base + endpoint
        headers = {"Authorization": f"Bearer {self.token}"}

        # Simulated network request
        print(f"[GoogleDrive] {method} {url} headers={headers} kwargs={kwargs}")
        if "fail" in kwargs:
            raise GoogleDriveAPIError("Simulated Google Drive API failure")
        return {"status": "success", "url": url, "method": method, "params": kwargs, "service": "GoogleDrive"}