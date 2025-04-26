import pytest
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))
from app.core.api.api_client import APIClientError, RateLimitExceeded
from app.core.api.deepseek_client import DeepSeekClient, DeepSeekAPIError
from app.core.api.google_drive_client import GoogleDriveClient, GoogleDriveAPIError

# ---- Test configs ----
DEEPSEEK_FAKE_KEY = "deepseek-key-123"
GDRIVE_FAKE_CREDENTIALS = {"access_token": "fake-gdrive-token"}

def test_deepseek_authentication():
    client = DeepSeekClient(api_key=DEEPSEEK_FAKE_KEY)
    client.authenticate()
    assert client.token == DEEPSEEK_FAKE_KEY

def test_google_drive_authentication():
    client = GoogleDriveClient(credentials=GDRIVE_FAKE_CREDENTIALS)
    client.authenticate()
    assert client.token == GDRIVE_FAKE_CREDENTIALS["access_token"]

def test_deepseek_success_request_is_cached():
    client = DeepSeekClient(api_key=DEEPSEEK_FAKE_KEY, cache_ttl=10)
    response1 = client.request("GET", "mock_endpoint")
    response2 = client.request("GET", "mock_endpoint")
    assert response1 is response2  # should be from cache

def test_google_drive_success_request_is_cached():
    client = GoogleDriveClient(credentials=GDRIVE_FAKE_CREDENTIALS, cache_ttl=10)
    response1 = client.request("GET", "mock_endpoint")
    response2 = client.request("GET", "mock_endpoint")
    assert response1 is response2

def test_deepseek_error_handling():
    client = DeepSeekClient(api_key=DEEPSEEK_FAKE_KEY)
    # Ensure cache is clear and use unique endpoint to avoid cache
    client.clear_cache()
    with pytest.raises(DeepSeekAPIError):
        client.request("GET", "will_fail_deepseek", fail=True)

def test_google_drive_error_handling():
    client = GoogleDriveClient(credentials=GDRIVE_FAKE_CREDENTIALS)
    # Ensure cache is clear and use unique endpoint to avoid cache
    client.clear_cache()
    with pytest.raises(GoogleDriveAPIError):
        client.request("GET", "will_fail_gdrive", fail=True)

def test_deepseek_rate_limit():
    client = DeepSeekClient(api_key=DEEPSEEK_FAKE_KEY)
    client._rate_limit = 2
    client._rate_period = 1
    # First two calls should be fine
    client.request("GET", "ep1-1")
    client.request("GET", "ep1-2")
    # Third call immediately should raise
    with pytest.raises(RateLimitExceeded):
        client.request("GET", "ep1-3")

def test_google_drive_rate_limit():
    client = GoogleDriveClient(credentials=GDRIVE_FAKE_CREDENTIALS)
    client._rate_limit = 2
    client._rate_period = 1
    client.clear_cache()
    client.request("GET", "gdrv_rl1")
    client.request("GET", "gdrv_rl2")
    with pytest.raises(RateLimitExceeded):
        client.request("GET", "gdrv_rl3")

def test_rate_limit_resets_after_period():
    client = DeepSeekClient(api_key=DEEPSEEK_FAKE_KEY)
    client._rate_limit = 1
    client._rate_period = 1
    client.request("GET", "foo")
    # After waiting for time window to pass, should be allowed
    time.sleep(1.1)
    client.request("GET", "foo2")

def test_clearing_cache():
    client = DeepSeekClient(api_key=DEEPSEEK_FAKE_KEY, cache_ttl=10)
    client.request("GET", "needs_cache_clear")
    assert client.get_cache(("GET", "needs_cache_clear")) is not None
    client.clear_cache()
    assert client.get_cache(("GET", "needs_cache_clear")) is None
