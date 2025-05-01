# File: /app/core/ai/resource_discovery.py
# This is the entry point/orchestrator for external resource discovery (Task 13.3).
# It leverages provider plugins, scoring, and mapping to course content.

from app.core.external_resources import ExternalResourceManager
from app.core.external_resources.scoring import score_resource
from app.models.course import Course

class ResourceDiscovery:
    def __init__(self, providers=None):
        self.manager = ExternalResourceManager(providers)
    
    def discover_resources(self, course: Course, max_results=10):
        """
        Find relevant external resources for the given course.
        Returns a list of (resource, score) tuples.
        """
        discovered = self.manager.query_all_providers(course)
        # Score all resources
        scored = [(res, score_resource(res, course)) for res in discovered]
        # Sort and filter by descending score
        scored = sorted(scored, key=lambda x: x[1], reverse=True)
        return scored[:max_results]
    
    def integrate_resources(self, course: Course):
        """
        Integrate discovered resources into the course's metadata or recommendations.
        """
        resources = self.discover_resources(course)
        self.manager.attach_resources_to_course(course, resources)
        return resources

# Usage:
# discovery = ResourceDiscovery()
# resources = discovery.discover_resources(course)
