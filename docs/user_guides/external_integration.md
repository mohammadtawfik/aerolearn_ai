# User Guide: External Resource Integration

## What is External Resource Integration?

The platform can automatically discover, evaluate, and integrate high-quality third-party resources (such as datasets, scholarly articles, videos, and tutorials) to enhance your course content.

## Getting Started

1. **Set up your API key:**  
   Configure your DeepSeek (or other provider) API key in `/app/core/config/api_secrets.py` following the project's security guidelines.

2. **Install dependencies:**  
   Ensure all required packages are installed:
   ```bash
   pip install requests
   ```

3. **Use the discovery interface:**  
   ```python
   from app.core.ai.resource_discovery import ResourceDiscovery
   
   # Initialize the discovery engine
   discovery = ResourceDiscovery()
   
   # Find relevant resources for a course
   resources = discovery.discover_resources(course)
   
   # Integrate resources with your course
   discovery.integrate_resources(course, resources)
   ```

## Integration Workflow

1. **Discovery:** The system searches across configured providers for relevant content.
2. **Scoring:** Resources are automatically ranked by relevance and quality.
3. **Review:** Optionally review suggested resources before integration.
4. **Access:** Integrated resources are available via `course.external_resources`.

## For Administrators

### Adding New Resource Providers

1. Create a provider subclass in `providers.py`:
   ```python
   class YouTubeProvider(BaseResourceProvider):
       def fetch_resources(self, course):
           # Implementation details
           return resources_list
   ```

2. Register your provider in `load_default_providers()`.

### Customizing Resource Scoring

- Edit scoring algorithms in `scoring.py`
- Implement ML-based scoring by extending the `ResourceScorer` class
- Configure minimum score thresholds in your application settings

### Bulk Operations

For scheduled enrichment of multiple courses:
```python
for course in Course.get_all_active():
    ResourceDiscovery().discover_and_integrate(course)
```

## Troubleshooting

- **No results returned?** Verify your API key and network connectivity.
- **Provider errors?** Check system logs for detailed error messages.
- **Poor quality resources?** Adjust scoring parameters or increase `min_score`.
- **Rate limiting?** Implement request throttling or upgrade API tier.

## Where to Get Help

- [API Reference Documentation](../api/resource_discovery_api.md)
- Contact system administrators for account-specific issues
- Submit feature requests or bug reports through the project issue tracker
