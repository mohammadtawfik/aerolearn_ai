from typing import Optional, Dict

class UserProfile:
    """
    Represents the user's profile and identity attributes.
    """
    def __init__(self, user_id: str, username: str, full_name: str = "", email: str = "", roles: Optional[list] = None, extra: Optional[Dict] = None):
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.roles = roles if roles is not None else []
        self.extra = extra if extra is not None else {}
        
    @property
    def role(self):
        """Return the primary role (string) for backward compatibility."""
        if self.roles:
            return self.roles[0]
        # Optionally support legacy (single-role) usage via extra
        return self.extra.get("role", None)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "roles": self.roles,
            "extra": self.extra
        }

    @staticmethod
    def from_dict(data: dict) -> "UserProfile":
        return UserProfile(
            user_id=data.get("user_id"),
            username=data.get("username"),
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            roles=data.get("roles", []),
            extra=data.get("extra", {}),
        )
