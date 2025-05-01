import pytest
from PyQt6.QtWidgets import QApplication

from app.ui.student.widgets.progress_visualization import ProgressVisualizationWidget
from app.models.progress import ProgressTimeline, ProgressEntry, ProgressMetricType, ComparativeProgress

import sys

@pytest.fixture
def qt_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_widget_creates_with_sample_data(qt_app):
    timeline = ProgressTimeline("user123", "courseABC")
    timeline.add_entry(ProgressEntry(ProgressMetricType.COMPLETION_PERCENTAGE, 10, None))
    timeline.add_entry(ProgressEntry(ProgressMetricType.COMPLETION_PERCENTAGE, 60, None))
    timeline.add_entry(ProgressEntry(ProgressMetricType.COMPLETION_PERCENTAGE, 90, None))

    comparative = ComparativeProgress(ProgressMetricType.COMPLETION_PERCENTAGE)
    comparative.set_value("user123", 90)
    comparative.set_value("user456", 80)

    widget = ProgressVisualizationWidget(timeline, comparative=comparative)
    assert widget.timeline.user_id == "user123"
    assert widget.comparative is not None
