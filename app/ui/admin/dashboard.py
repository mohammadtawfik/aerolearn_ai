from app.core.auth.authentication import AdminAuthService, AdminPermissions
from app.core.auth.session import SessionManager
from app.models.user import User

class AdminDashboard:
    def __init__(self, session_manager=None):
        self.session_manager = session_manager or SessionManager()
        self.auth_service = AdminAuthService()

    def render(self, session_token:str) -> str:
        session = self.session_manager.get_session(session_token)
        if not session or not self.auth_service.enforce_permission(session, AdminPermissions.DASHBOARD_VIEW):
            return "<h1>Access Denied</h1>"

        nav = self.get_navigation(session)
        content = "<div>Welcome, Admin!</div>"  # Placeholder for main content
        return f"""
        <div class='admin-nav'>{nav}</div>
        <div class='admin-content'>{content}</div>
        """

    def get_navigation(self, session):
        items = []
        perms = [
            (AdminPermissions.USER_MANAGEMENT, "User Management"),
            (AdminPermissions.COURSE_MANAGEMENT, "Course Management"),
            (AdminPermissions.SYSTEM_MONITOR, "System Monitor"),
            (AdminPermissions.SECURITY_CONFIG, "Security Settings")
        ]
        for perm, label in perms:
            if self.auth_service.enforce_permission(session, perm):
                items.append(f"<a href='#{perm}'>{label}</a>")
        return " | ".join(items)

    # Extend: route to subpages, integrate component registry/navigation, etc.