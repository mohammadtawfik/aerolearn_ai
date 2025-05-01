
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User
from app.models.course import Course, Enrollment, EnrollmentStatus
from app.core.enrollment.enrollment_service import EnrollmentService

# Debug print to confirm which Course class is imported
print("USING `Course` FROM:", Course, "MODULE:", Course.__module__)
print("HAS '__table__':", hasattr(Course, "__table__"))
print("MRO:", Course.__mro__)

# Use SQLite in-memory database for testing
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session (and schema) for each test."""
    engine = create_engine(TEST_DB_URL, echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    # clear_mappers()  # <-- Removed per ORM mapping safety

@pytest.fixture
def dummy_user(db_session):
    user = User(username="student1", email="student1@ex.com")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def dummy_approver(db_session):
    approver = User(username="prof1", email="prof1@ex.com", role="admin")
    db_session.add(approver)
    db_session.commit()
    return approver

@pytest.fixture
def dummy_course(db_session):
    course = Course(title="Intro AI", description="AI basics")
    db_session.add(course)
    db_session.commit()
    return course

@pytest.fixture
def service(db_session, dummy_course):
    return EnrollmentService(db_session=db_session)

def test_request_enrollment(service, db_session, dummy_user, dummy_course):
    req = service.request_enrollment(dummy_course.id, dummy_user.id)
    assert req is not None
    assert req.status == EnrollmentStatus.PENDING

def test_approve_enrollment(service, db_session, dummy_user, dummy_approver, dummy_course):
    service.request_enrollment(dummy_course.id, dummy_user.id)
    req = service.approve_enrollment(dummy_course.id, dummy_user.id, dummy_approver.id)
    assert req.status == EnrollmentStatus.APPROVED
    assert req.approved_by == dummy_approver.id

def test_reject_enrollment(service, db_session, dummy_user, dummy_approver, dummy_course):
    service.request_enrollment(dummy_course.id, dummy_user.id)
    req = service.reject_enrollment(dummy_course.id, dummy_user.id, dummy_approver.id)
    assert req.status == EnrollmentStatus.REJECTED
    assert req.approved_by == dummy_approver.id

def test_cancel_enrollment(service, db_session, dummy_user, dummy_course):
    service.request_enrollment(dummy_course.id, dummy_user.id)
    req = service.cancel_enrollment(dummy_course.id, dummy_user.id)
    assert req.status == EnrollmentStatus.CANCELLED

def test_get_enrollment_status(service, db_session, dummy_user, dummy_approver, dummy_course):
    service.request_enrollment(dummy_course.id, dummy_user.id)
    service.approve_enrollment(dummy_course.id, dummy_user.id, dummy_approver.id)
    status = service.get_enrollment_status(dummy_course.id, dummy_user.id)
    assert status == EnrollmentStatus.APPROVED
