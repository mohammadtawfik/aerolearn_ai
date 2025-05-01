# Progress Metrics API

*Location: `/docs/api/progress_metrics.md`*

**Updated for PyQt6 and final model/widget integration.**

## Overview

This document specifies the standardized models and widgets for student progress tracking and visualization in AeroLearn AI.

## Progress Metrics

### `ProgressMetricType`
- **completion_percentage** — Percent of course/module completed
- **time_spent** — Total time spent (minutes/hours)
- **grade** — Current/Latest grade (0–100)
- **attempts** — Number of quiz attempts

## Data Models

### `ProgressEntry`
| Field     | Type               | Description                  |
|-----------|--------------------|-----------------------------|
| metric    | ProgressMetricType | Metric identifier           |
| value     | float              | Metric value (0-100, etc.)  |
| timestamp | datetime           | When value was recorded     |

### `ProgressTimeline`
- Ordered list of `ProgressEntry` for user/content.
- Supports charts, time-series, and custom aggregations.

### `ComparativeProgress`
- Cross-user or cross-group comparison.
- Used for bar charts and other comparative analyses.

## Widgets

### `ProgressVisualizationWidget`
_Modern PyQt6/QCharts-based: see `/app/ui/student/widgets/progress_visualization.py`._
- Accepts `ProgressTimeline` for line charts, progress bars.
- Accepts `ComparativeProgress` for bar chart comparisons.
- Plug-in ready for the dashboard (`/app/ui/student/dashboard.py`).

## Integration
- Load data using either sample generators (testing) or by connecting to real course/user/DB logic.
- See `/app/models/progress.py` for model usage.
- Register widget through `/app/ui/student/register_widgets.py`.

## Migration Note

UI uses **PyQt6 + PyQt6-Charts**. Update any local environments and requirements accordingly.

## Example

```python
from app.models.progress import ProgressTimeline, ProgressEntry, ProgressMetricType

# Create a timeline for a specific user and module
timeline = ProgressTimeline("user789", "moduleXYZ")
timeline.add_entry(ProgressEntry(ProgressMetricType.COMPLETION_PERCENTAGE, 30))
timeline.add_entry(ProgressEntry(ProgressMetricType.COMPLETION_PERCENTAGE, 60))
timeline.add_entry(ProgressEntry(ProgressMetricType.COMPLETION_PERCENTAGE, 100))

# Display in a widget
from app.ui.student.widgets.progress_visualization import ProgressVisualizationWidget
widget = ProgressVisualizationWidget()
widget.display_timeline(timeline)
```

---
