# Location: /app/core/config/api_secrets.py
# DO NOT CHECK THIS FILE INTO VERSION CONTROL!
# This file provides access to the AI API Key for integration and real (not mock) tests.
# Set your actual key here or (preferably) use an environment variable for security.

import os

# Option 1: Prefer environment variable
AI_API_KEY = os.environ.get("AI_API_KEY")

# Option 2: (Fallback for testing) - uncomment and paste your key
AI_API_KEY = "sk-da8169d57c5b4bf6812a02b924492b09"

if not AI_API_KEY:
    raise RuntimeError(
        "AI_API_KEY is not set! Set the environment variable 'AI_API_KEY' "
        "or provide it directly in this file (NOT recommended for shared or production use)."
    )