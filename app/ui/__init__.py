# /app/ui/__init__.py
"""
UI package initialization.

Ensures the UI module is recognized by the Python import system.
This is required for:
 - Protocol-compliant modularity
 - Import hygiene across tests and implementations
 - Compatibility with automation, unit, and integration tests

Mandated by project structure as seen in code_summary.md and to align with best practices (see also: /docs/development/day22_plan.md advisory on import hygiene).
"""