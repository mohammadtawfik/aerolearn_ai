import pytest
from app.core.auth.authentication import AdminAuthService, AdminPermissions
from app.core.auth.authorization import AuthorizationManager

# --- TEST DUMMY CLASSES ---

class DummyUserProfile:
    def __init__(self, user_id, username=None, role=None, full_name=None, email=None, bio="", expertise_level=None):
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self.email = email
        if role:
            self.roles = [role]
        else:
            self.roles = []
        self.bio = bio
        self.expertise_level = expertise_level

    @property
    def role(self):
        if self.roles:
            return self.roles[0]
        return None

class DummyCredentialManager:
    """Minimal test stub for credential checking."""
    def verify_password(self, user_id, password):
        # Accept 'correct_pw' as valid, anything else as invalid.
        return password == "correct_pw"

class DummyUserModel:
    """Minimal stub matching UserModel API/behavior for testing."""
    def __init__(self, id, username, role='admin', mfa_secret='secret', password_hash='hashed_pw'):
        self.id = id
        self.username = username
        self.role = role
        self.mfa_secret = mfa_secret
        self.password_hash = password_hash

    @classmethod
    def get_user_by_username(cls, username):
        if username == 'admin':
            user = cls(id="1", username="admin", role="admin", mfa_secret="secret")
            # Make sure role is registered, and assign to user for AuthorizationManager
            AuthorizationManager.register_role('admin', [
                "admin_dashboard:view", "admin:user_manage", "admin:course_manage", "admin:system_monitor"
            ])
            AuthorizationManager.assign_role_to_user(user.id, "admin")
            return user
        return None

    def is_admin(self):
        return self.role in ("admin", "superadmin")

@pytest.fixture(autouse=True)
def user_profile_patch(monkeypatch):
    # Patch UserProfile used by authentication to our DummyUserProfile
    import app.core.auth.user_profile as user_profile_mod
    monkeypatch.setattr(user_profile_mod, "UserProfile", DummyUserProfile)
    yield

@pytest.fixture
def auth_service():
    return AdminAuthService(user_model_cls=DummyUserModel, cred_manager=DummyCredentialManager())

@pytest.fixture
def dummy_admin_user():
    return DummyUserModel(id='1', username='admin', role='admin', mfa_secret='secret')

def test_fail_with_wrong_password(auth_service, dummy_admin_user):
    session = auth_service.authenticate_admin("admin", "wrong_pw", "123456")
    assert session is None

def test_fail_with_wrong_mfa(auth_service, monkeypatch, dummy_admin_user):
    # Patch MFAProvider.verify_code to return False
    import app.core.auth.authentication as auth_mod
    monkeypatch.setattr(auth_mod.MFAProvider, "verify_code", lambda self, code, window=1: False)
    session = auth_service.authenticate_admin("admin", "correct_pw", "badcode")
    assert session is None

def test_successful_admin_login(monkeypatch, auth_service, dummy_admin_user):
    import app.core.auth.authentication as auth_mod
    monkeypatch.setattr(auth_mod.MFAProvider, "verify_code", lambda self, code, window=1: True)
    session = auth_service.authenticate_admin("admin", "correct_pw", "123456")
    assert session is not None
    assert session.profile.role == "admin"

def test_dashboard_permission_enforcement(monkeypatch, auth_service, dummy_admin_user):
    import app.core.auth.authentication as auth_mod
    monkeypatch.setattr(auth_mod.MFAProvider, "verify_code", lambda self, code, window=1: True)
    session = auth_service.authenticate_admin("admin", "correct_pw", "123456")
    assert auth_service.enforce_permission(session, AdminPermissions.DASHBOARD_VIEW)
