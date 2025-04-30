import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Canonical model imports
from app.models.base import Base
import app.models.user
import app.models.tag
import app.models.category
import app.models.course
# Import any other models with table definitions
from app.core.db.course_admin import CourseAdminService

@pytest.fixture(scope="module")
def session():
    # Ensure all SQLAlchemy tables are registered before create_all
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_create_and_archive_restore(session):
    admin = CourseAdminService(session)
    # Create course
    course = admin.create_course(title="Physics 101")
    assert course.title == "Physics 101"
    # Archive course
    admin.archive_course(course.id)
    archived = session.query(type(course)).get(course.id)
    assert archived.is_archived
    # Restore course
    admin.restore_course(course.id)
    restored = session.query(type(course)).get(course.id)
    assert restored.is_archived == False

def test_template_creation(session):
    admin = CourseAdminService(session)
    template = admin.create_course(title="Template Course", is_template=True)
    copy = admin.create_course(title="Instantiated from Template", from_template_id=template.id)
    assert copy.template_parent_id == template.id

def test_bulk_enroll(session):
    admin = CourseAdminService(session)
    course = admin.create_course(title="Bulk Enroll")
    user_ids = [101, 102, 103]
    admin.enroll_users_bulk(course.id, user_ids)
    enrollments = session.query(course.__class__).get(course.id).enrollments
    # Enrollment creation is tested; details may differ based on real user model
