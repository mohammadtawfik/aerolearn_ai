# File: /app/core/external_resources/__init__.py
# This package handles external resource provider plugins, resource abstractions, and management.

from typing import List, Any
from .providers import BaseResourceProvider

class ExternalResourceManager:
    def __init__(self, providers=None):
        # If no providers, load all available ones
        self.providers: List[BaseResourceProvider] = providers or BaseResourceProvider.load_default_providers()
    
    def query_all_providers(self, course) -> List[Any]:
        """
        Ask each provider for resources relevant to the course.
        Returns a flat list of resources.
        """
        resources = []
        for provider in self.providers:
            try:
                resources.extend(provider.fetch_resources(course))
            except Exception as e:
                # Log and skip failed provider
                print(f"[WARN] Provider {provider.__class__.__name__} failed: {e}")
        return resources
    
    def attach_resources_to_course(self, course, resources):
        """
        Attaches resources (with scoring) to the course (e.g., as recommendations).
        This could modify metadata or update the course DB as needed.
        """
        # This should use Course API/model hooks
        if hasattr(course, 'external_resources'):
            course.external_resources = [r[0] for r in resources]
        else:
            setattr(course, 'external_resources', [r[0] for r in resources])

        # Integrate with course.save() or emit event as required
        return True