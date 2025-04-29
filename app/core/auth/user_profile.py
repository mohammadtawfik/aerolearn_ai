from typing import Optional, Dict, List, Any

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


class UserProfileManager:
    """
    Core logic for user profile management (CRUD, validation, bulk ops).
    """

    def __init__(self):
        # Replace this with actual DB/session/model as needed.
        self.users = {}  # user_id -> UserProfile object
        self.next_id = 1

    def _validate_user_data(self, data: Dict[str, Any], is_update=False) -> bool:
        """
        Validate user profile data. Returns True if valid, False otherwise.
        Raises ValueError for invalid cases.
        """
        required_fields = ['username', 'email']
        for field in required_fields:
            if not is_update and field not in data:
                raise ValueError(f"Missing required field: {field}")
            if field in data and not data[field]:
                raise ValueError(f"Field '{field}' cannot be empty")
        
        # Email format validation
        if 'email' in data and data['email']:
            if '@' not in data['email'] or '.' not in data['email']:
                raise ValueError("Invalid email format")
                
        return True

    def create_user(self, profile_data: Dict[str, Any]) -> str:
        """
        Create a new user profile and return the user_id.
        """
        self._validate_user_data(profile_data)
        user_id = str(self.next_id)
        self.next_id += 1
        
        # Create UserProfile object
        profile = UserProfile(
            user_id=user_id,
            username=profile_data.get('username'),
            full_name=profile_data.get('full_name', ''),
            email=profile_data.get('email', ''),
            roles=profile_data.get('roles', []),
            extra=profile_data.get('extra', {})
        )
        
        self.users[user_id] = profile
        return user_id

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user profile by user_id. Return dict or None.
        """
        user = self.users.get(user_id)
        return user.to_dict() if user else None

    def update_user(self, user_id: str, update_fields: Dict[str, Any]) -> bool:
        """
        Update a user profile with the provided fields.
        Returns True if successful, False if user not found.
        """
        if user_id not in self.users:
            return False
            
        self._validate_user_data(update_fields, is_update=True)
        user = self.users[user_id]
        
        # Update fields
        if 'username' in update_fields:
            user.username = update_fields['username']
        if 'full_name' in update_fields:
            user.full_name = update_fields['full_name']
        if 'email' in update_fields:
            user.email = update_fields['email']
        if 'roles' in update_fields:
            user.roles = update_fields['roles']
        if 'extra' in update_fields:
            user.extra.update(update_fields['extra'])
            
        return True

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user profile by user_id.
        Returns True if successful, False if user not found.
        """
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    def list_users(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all users, optionally filtered by the provided criteria.
        Returns list of user dicts.
        """
        if not filters:
            return [u.to_dict() for u in self.users.values()]
            
        result = []
        for user in self.users.values():
            match = True
            for key, value in filters.items():
                if key == 'roles' and value:
                    # Check if any of the filter roles match any user roles
                    if not any(role in user.roles for role in value):
                        match = False
                        break
                elif hasattr(user, key) and getattr(user, key) != value:
                    match = False
                    break
                elif key in user.extra and user.extra[key] != value:
                    match = False
                    break
            
            if match:
                result.append(user.to_dict())
                
        return result
        
    def bulk_create_users(self, profiles_data: List[Dict[str, Any]]) -> List[str]:
        """
        Create multiple user profiles at once.
        Returns a list of created user_ids.
        """
        user_ids = []
        for profile_data in profiles_data:
            try:
                user_id = self.create_user(profile_data)
                user_ids.append(user_id)
            except ValueError as e:
                # Log the error but continue with other profiles
                print(f"Error creating user: {e}")
        
        return user_ids
        
    def bulk_update_users(self, updates: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """
        Update multiple user profiles at once.
        Takes a dictionary mapping user_ids to update data.
        Returns a dictionary mapping user_ids to success status.
        """
        results = {}
        for user_id, update_data in updates.items():
            results[user_id] = self.update_user(user_id, update_data)
        
        return results
        
    def bulk_delete_users(self, user_ids: List[str]) -> Dict[str, bool]:
        """
        Delete multiple user profiles at once.
        Returns a dictionary mapping user_ids to success status.
        """
        results = {}
        for user_id in user_ids:
            results[user_id] = self.delete_user(user_id)
            
        return results
