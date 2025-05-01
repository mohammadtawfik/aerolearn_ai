"""
File: /app/core/search/permissions.py
Purpose: Filtering search results by user permissions

This file should be saved as /app/core/search/permissions.py according to the project structure.
"""

def filter_by_permission(user, results):
    """
    Returns only items user is allowed to see based on permissions.
    Placeholder: expects each result to have 'data' dict with 'permissions' list.
    """
    allowed = []
    user_permissions = set(getattr(user, 'permissions', []))
    for result in results:
        perms = set(result['data'].get('permissions', []))
        # Allow if no restriction, or intersection exists
        if not perms or user_permissions & perms:
            allowed.append(result)
    return allowed