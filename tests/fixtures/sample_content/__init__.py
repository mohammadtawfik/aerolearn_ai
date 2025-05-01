"""
Provides test fixtures: create_sample_course_content and external_resource_fixtures
for resource discovery integration testing.
"""

from collections import namedtuple

# Use a simple namedtuple or dataclass for sample course content
CourseContent = namedtuple("CourseContent", ["title", "description", "modules"])

def create_sample_course_content():
    """
    Returns a list of sample course content items,
    covering normal cases and an edge case for 'muon tomography'.
    """
    return [
        CourseContent(
            title="Introduction to Aerodynamics",
            description="Covers the basics of airflow, lift, drag, and airfoil design.",
            modules=[
                {"title": "Airfoils", "lessons": ["Shapes and Properties", "Applications"]},
                {"title": "Drag and Lift", "lessons": ["Introduction", "Practical Calculation"]}
            ]
        ),
        CourseContent(
            title="Jet Engine Fundamentals",
            description="An overview of jet engine principles, thermodynamics, and applications.",
            modules=[
                {"title": "Jet Engine Types", "lessons": ["Turbofan", "Turbojet"]},
                {"title": "Thermodynamics", "lessons": ["Cycles", "Real-world Effects"]}
            ]
        ),
        CourseContent(
            title="Muon Tomography in Aerospace",
            description="A rare and advanced topic for edge-case testing in resource discovery.",
            modules=[
                {"title": "Muon Detectors", "lessons": ["Detector Physics", "Data Processing"]}
            ]
        )
    ]

# Sample external resource fixture data to mimic what providers would return (as dicts)
external_resource_fixtures = [
    {
        "title": "Aerodynamics Explained",
        "url": "https://example.com/resources/aero_explained",
        "description": "Detailed resource on aerodynamic principles.",
        "score": 0.8,
        "quality": "high",
        "metadata": {"source": "MockProvider"}
    },
    {
        "title": "Jet Engine Operation",
        "url": "https://example.com/resources/jet_engines",
        "description": "A walk through jet engine technology with diagrams.",
        "score": 0.9,
        "quality": "high",
        "metadata": {"source": "MockProvider"}
    },
    {
        "title": "Muon Tomography Applications",
        "url": "https://example.com/resources/muon_tomo",
        "description": "Explains the use of muon tomography in aerospace.",
        "score": 0.95,
        "quality": "high",
        "metadata": {"source": "MockProvider"}
    },
]
