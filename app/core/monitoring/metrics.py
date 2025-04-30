"""
System Metrics & Alert Manager — AeroLearn AI
Save at: /app/core/monitoring/metrics.py

Features:
- Define metrics types and schema
- Register/report metrics for components
- Threshold-based alerting (with callback hooks)
- Real-time status query API
"""

from enum import Enum
from typing import Dict, Any, Callable, List, Optional
import threading
import time

class MetricType(Enum):
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    UPTIME = "uptime"
    UNRESPONSIVE_COMPONENTS = "unresponsive_components"
    CUSTOM = "custom"

class AlertLevel(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"

class Metric:
    def __init__(self, name: str, type_: MetricType, value: Any, timestamp: float = None):
        if not isinstance(type_, MetricType):
            # Accept int (enum index) or string (enum member name)
            if isinstance(type_, int):
                try:
                    type_ = list(MetricType)[type_]
                except IndexError:
                    type_ = MetricType.CUSTOM
            elif isinstance(type_, str):
                try:
                    type_ = MetricType[type_.upper()]
                except KeyError:
                    type_ = MetricType.CUSTOM
        self.name = name
        self.type = type_
        self.value = value
        self.timestamp = timestamp if timestamp else time.time()

    def to_dict(self):
        return dict(
            name=self.name,
            type=self.type.value if isinstance(self.type, MetricType) else self.type,
            value=self.value,
            timestamp=self.timestamp,
        )

class MetricAlert:
    def __init__(self, metric_name: str, level: AlertLevel, threshold: Any, callback: Optional[Callable]=None):
        self.metric_name = metric_name
        self.level = level
        self.threshold = threshold
        self.callback = callback

class SystemMetricsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._metrics: Dict[str, Metric] = {}  # key: metric name
        self._alerts: List[MetricAlert] = []
        self._lock = threading.Lock()

    def register_metric(self, metric: Metric):
        with self._lock:
            self._metrics[metric.name] = metric
            self._check_alerts(metric)

    def report_metric(self, name: str, type_: MetricType, value: Any):
        metric = Metric(name, type_, value)
        self.register_metric(metric)

    def get_metric(self, name: str) -> Optional[Metric]:
        return self._metrics.get(name, None)

    def get_all_metrics(self) -> Dict[str, Metric]:
        return dict(self._metrics)

    def register_alert(self, alert: MetricAlert):
        with self._lock:
            self._alerts.append(alert)
            
    def get_alerts_for_metric(self, metric_name: str) -> List[MetricAlert]:
        """Returns all alert registrations for a given metric name."""
        return [alert for alert in self._alerts if alert.metric_name == metric_name]

    def _check_alerts(self, metric: Metric):
        for alert in self._alerts:
            if alert.metric_name != metric.name:
                continue
            trig = False
            # For numeric thresholds
            try:
                if isinstance(metric.value, (int, float)) and isinstance(alert.threshold, (int, float)):
                    if alert.level == AlertLevel.WARNING and metric.value >= alert.threshold:
                        trig = True
                    elif alert.level == AlertLevel.CRITICAL and metric.value >= alert.threshold:
                        trig = True
                # For other (e.g., unresponsive_components: list length)
                elif alert.level == AlertLevel.CRITICAL and isinstance(metric.value, list) and len(metric.value) >= alert.threshold:
                    trig = True
            except Exception:
                pass
            if trig and alert.callback:
                try:
                    alert.callback(metric, alert.level)
                except Exception:
                    pass  # Optionally log
    # Optionally: schedule periodic polling (not included here for simplicity)

system_metrics = SystemMetricsManager()
