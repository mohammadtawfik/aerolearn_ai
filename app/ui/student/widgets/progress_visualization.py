"""
app/ui/student/widgets/progress_visualization.py
===============================================

Widget for visualizing student progress:
- Progress bars for module/lesson
- Line/bar charts for time-series and comparisons

Location: app/ui/student/widgets/progress_visualization.py
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QBarSeries, QBarSet, QCategoryAxis
from PyQt6.QtCore import Qt

from app.models.progress import ProgressTimeline, ProgressMetricType, ComparativeProgress

class ProgressVisualizationWidget(QWidget):
    """
    Visualization widget for student progress, supporting multiple metrics.
    """

    def __init__(self, timeline: ProgressTimeline, comparative: ComparativeProgress = None, parent=None):
        super().__init__(parent)
        self.timeline = timeline
        self.comparative = comparative
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Progress Overview"))

        # Progress Bar for Completion
        completion_entries = self.timeline.get_metric_over_time(ProgressMetricType.COMPLETION_PERCENTAGE)
        if completion_entries:
            latest = completion_entries[-1].value
            pb = QProgressBar()
            pb.setRange(0, 100)
            pb.setValue(int(latest))
            pb.setFormat(f"Complete: {int(latest)}%")
            layout.addWidget(pb)

        # Time-series Line Chart
        if completion_entries and len(completion_entries) > 1:
            chart = QChart()
            series = QLineSeries()
            for entry in completion_entries:
                # Use integer timestamp for X, value for Y
                x = entry.timestamp.timestamp()
                y = entry.value
                series.append(x, y)
            chart.addSeries(series)
            axisX = QCategoryAxis()
            axisX.setTitleText("Time")
            chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axisX)
            chart.setTitle("Completion over Time")
            chart_view = QChartView(chart)
            layout.addWidget(chart_view)

        # Comparative Bar Chart
        if self.comparative:
            bar_series = QBarSeries()
            bar_set = QBarSet(self.comparative.metric.value)
            categories = list(self.comparative.values.keys())
            for entity_id in categories:
                bar_set.append(self.comparative.values[entity_id])
            bar_series.append(bar_set)

            chart = QChart()
            chart.addSeries(bar_series)
            axisX = QCategoryAxis()
            for i, category in enumerate(categories):
                axisX.append(category, i+1)
            axisX.setTitleText("Students/Groups")
            chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
            bar_series.attachAxis(axisX)
            chart.setTitle(f"{self.comparative.metric.value} Comparison")
            chart_view = QChartView(chart)
            layout.addWidget(chart_view)

        self.setLayout(layout)
