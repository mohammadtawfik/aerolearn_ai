"""
Location: /scripts/admin_interface_selftest.py
(Chosen according to implementation plan in docs/development/day11_done_criteria.md.)

Runs a sequence of admin operations, printing status for review.
Intended for dry-run, manual, or CI use for Task 11.5 verification.
"""

from app.core.auth.user_profile import UserProfile
from app.core.db.course_admin import CourseAdmin
from app.core.monitoring.settings_manager import SettingsManager
from app.models.user import User
from app.models.course import Course

def print_result(title, passed):
    print(f"{title:50s}: {'PASS' if passed else 'FAIL'}")

def run_admin_selftest():
    # Create test admin user/session
    admin = UserProfile(username="integration_admin", roles=["admin"])
    ca = CourseAdmin()
    sm = SettingsManager()
    passed = True

    # Test 1: User create/edit/role
    try:
        user = UserProfile(username="selftest1")
        admin.create_user(user)
        admin.assign_role(user, "student")
        logs = admin.get_user_logs(user)
        passed_test = user and "student" in user.roles and isinstance(logs, list)
        print_result("User management workflow", passed_test)
        passed = passed and passed_test
    except Exception as e:
        print_result("User management workflow", False)
        passed = False

    # Test 2: Course management/archiving
    try:
        course = Course(title="SelfTest Course")
        ca.create_course(course, created_by=admin)
        ca.archive_course(course)
        archived = getattr(course, "is_archived", False)
        ca.restore_course(course)
        restored = not getattr(course, "is_archived", True)
        passed_test = archived and restored
        print_result("Course archiving/restoration", passed_test)
        passed = passed and passed_test
    except Exception as e:
        print_result("Course archiving/restoration", False)
        passed = False

    # Test 3: Config/monitoring
    try:
        sm.set_setting("maintenance_mode", True)
        value = sm.get_setting("maintenance_mode")
        passed_test = (value is True)
        print_result("System config change", passed_test)
        sm.set_setting("maintenance_mode", False)  # reset
        passed = passed and passed_test
    except Exception as e:
        print_result("System config change", False)
        passed = False

    # Summary
    print("\nAdmin self-test " + ("SUCCEEDED" if passed else "FAILED"))

if __name__ == "__main__":
    run_admin_selftest()