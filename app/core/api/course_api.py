"""
Location: /app/core/api/course_api.py (NEW FILE)

Provides REST API endpoints for course browsing, searching, enrollment request/approval/cancel,
integrating with EnrollmentService and Course model.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from app.core.enrollment.enrollment_service import EnrollmentService
from app.models.course import EnrollmentStatus

# In actual usage, course_store would be injected (e.g., from DB/session)
course_store = {}  # Placeholder for example purposes
enrollment_service = EnrollmentService(course_store)

router = APIRouter()

@router.get("/courses")
def browse_courses():
    """Browse all courses."""
    courses = enrollment_service.browse_courses()
    return [c.serialize() for c in courses]

@router.get("/courses/search")
def search_courses(query: str = Query(..., description="Course title or keyword")):
    """Search courses by keyword."""
    courses = enrollment_service.search_courses(query)
    return [c.serialize() for c in courses]

@router.post("/courses/{course_id}/enroll")
def request_enrollment(course_id: str, user_id: str = Body(..., embed=True)):
    """Request enrollment in a course."""
    req = enrollment_service.request_enrollment(course_id, user_id)
    if not req:
        raise HTTPException(status_code=404, detail="Course not found")
    return req.to_dict()

@router.post("/courses/{course_id}/enrollment/approve")
def approve_enrollment(course_id: str, user_id: str = Body(...), approver_id: str = Body(...)):
    """Approve a pending enrollment request."""
    req = enrollment_service.approve_enrollment(course_id, user_id, approver_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Enrollment request/course not found")
    return req.to_dict()

@router.post("/courses/{course_id}/enrollment/reject")
def reject_enrollment(course_id: str, user_id: str = Body(...), approver_id: str = Body(...)):
    """Reject an enrollment request."""
    req = enrollment_service.reject_enrollment(course_id, user_id, approver_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Enrollment request/course not found")
    return req.to_dict()

@router.post("/courses/{course_id}/enrollment/cancel")
def cancel_enrollment(course_id: str, user_id: str = Body(...)):
    """Cancel an enrollment request (by student)."""
    req = enrollment_service.cancel_enrollment(course_id, user_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Enrollment request/course not found")
    return req.to_dict()

@router.get("/courses/{course_id}/enrollment/status")
def get_enrollment_status(course_id: str, user_id: str = Query(...)):
    """Get current enrollment status for this user/course."""
    status = enrollment_service.get_enrollment_status(course_id, user_id)
    if status is None:
        raise HTTPException(status_code=404, detail="No such enrollment")
    return {"status": status}