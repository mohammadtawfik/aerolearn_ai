# Location: /app/core/config/api_secrets_example.py
# DO NOT PUT REAL KEYS HERE. This is a template for contributors.
# Copy to 'api_secrets.py' and fill in your own API key or use environment variable.

import os

AI_API_KEY = os.environ.get("AI_API_KEY") or "sk-da8169d57c5b4bf6812a02b924492b09"

# For security, DO NOT check the real 'api_secrets.py' into source control.