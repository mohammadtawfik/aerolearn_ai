"""
File: /tests/fixtures/sample_content/repositories.py

Purpose:
    Provides create_sample_repositories() for semantic search and integration tests.
    - Returns repositories (dict), users (dict by role), and a mock AuthorizationManagerClass
    - Ensures repositories contain the science content and keywords the tests check for
    - Content in flat dicts, not nested under 'data'

Per project structure (see code_summary.md), all test content/data factories go here.
"""

class MockAuthorizationManager:
    """
    Minimal mock of AuthorizationManagerClass—expand as needed for search permission logic.
    """
    def has_permission(self, user, permission):
        return permission in getattr(user, "permissions", [])

def create_sample_repositories():
    """
    Returns (repositories, users_dict, auth_manager_mock) for semantic search integration tests.
    
    Returns:
        (
            dict of sample repositories {
                "courses": [...], "lessons": [...], "docs": [...]
            },
            dict of users by role {'student': User, 'professor': User, etc.},
            MockAuthorizationManager instance
        )
    Includes content for all tested keywords: Quantum, Heisenberg, electron, user charge, etc.
    """
    repositories = {
        "courses": [
            {"id": "course1", "title": "Physics I", "description": "Introductory physics.", "permissions": ["content.view"]},
            {"id": "course2", "title": "Thermodynamics", "description": "Energy, heat, and entropy.", "permissions": ["content.view"]}
        ],
        "lessons": [
            {"id": "lesson1", "title": "Kinetic Energy", "content": "Explains kinetic energy in physics.", "permissions": ["content.view"]},
            {"id": "lesson2", "title": "Heat Transfer", "content": "Principles of heat transfer.", "permissions": ["content.view"]}
        ],
        "docs": [
            {"id": "doc1", "title": "Quantum Entanglement Experiments", "body": "Results of recent quantum entanglement experiments.", "content": "Quantum info science.", "summary": "", "permissions": ["content.view"]},
            {"id": "doc2", "title": "Heisenberg Uncertainty", "body": "Explains Heisenberg's famous uncertainty principle.", "content": "Measurement limitations in quantum systems.", "summary": "", "permissions": ["content.view"]},
            {"id": "doc3", "title": "Electron Charge", "body": "The electron's charge is fundamental.", "content": "Discusses charge of electron in physics.", "summary": "", "permissions": ["content.view"]},
            {"id": "doc4", "title": "User Charge Report", "body": "", "content": "", "summary": "Financial admin: user charge posted to account.", "permissions": ["user.manage"]},
            {"id": "doc5", "title": "Thermodynamics", "body": "Entropy and energy in systems.", "content": "Thermodynamic laws.", "summary": "", "permissions": ["content.view"]}
        ]
    }
    users = {
        "student": type("User", (), {
            "id": "student_user", 
            "roles": ["student"], 
            "permissions": ["content.view"]
        })(),
        "professor": type("User", (), {
            "id": "professor_user",
            "roles": ["professor"],
            "permissions": ["content.view", "content.edit"]
        })(),
        "admin": type("User", (), {
            "id": "admin_user",
            "roles": ["admin"],
            "permissions": ["content.view", "content.edit", "user.manage"]
        })(),
        "restricted": type("User", (), {
            "id": "restricted", 
            "roles": [], 
            "permissions": []
        })()
    }
    auth_manager = MockAuthorizationManager()
    return repositories, users, auth_manager
