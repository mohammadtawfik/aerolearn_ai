"""
System Metrics & Alert Manager — AeroLearn AI
Save at: /app/core/monitoring/metrics.py

Features:
- Define metrics types and schema
- Register/report metrics for components
- Threshold-based alerting (with callback hooks)
- Real-time status query API
- Learning analytics and progress tracking metrics
"""

from enum import Enum
from typing import Dict, Any, Callable, List, Optional, Set
import threading
import time
from datetime import datetime, timedelta

class MetricType(Enum):
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    UPTIME = "uptime"
    UNRESPONSIVE_COMPONENTS = "unresponsive_components"
    LEARNING_OBJECTIVE = "learning_objective"
    TIME_ON_TASK = "time_on_task"
    COMPLETION_RATE = "completion_rate"
    PERFORMANCE_TREND = "performance_trend"
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

# Learning Analytics Metrics

def track_learning_objective(user_id: str, objective_id: str, activities: List[Dict[str, Any]]) -> float:
    """
    Track the degree of achievement for a specific learning objective by user.
    
    :param user_id: User identifier
    :param objective_id: Learning objective identifier
    :param activities: List of activity logs relevant to the objective.
        Each activity should include: {"user_id":str, "objective_id":str, "completed":bool}
    :return: Completion ratio [0, 1]
    """
    # Filter for relevant activities for this user/objective
    relevant = [
        a for a in activities
        if a.get("user_id") == user_id and a.get("objective_id") == objective_id
    ]
    if not relevant:
        return 0.0
    completed_count = sum(1 for a in relevant if a.get("completed"))
    return completed_count / len(relevant)

def monitor_time_on_task(user_id: str, activity_logs: List[Dict[str, Any]]) -> timedelta:
    """
    Monitor total time on task for a user.
    
    :param user_id: User identifier
    :param activity_logs: List of logs with start/end times
        Each log should include: {"user_id":str, "start":ISO 8601 str, "end":ISO 8601 str}
    :return: Total duration on-task as timedelta
    """
    total = timedelta()
    for log in activity_logs:
        if log.get("user_id") != user_id:
            continue
        try:
            start = datetime.fromisoformat(log["start"])
            end = datetime.fromisoformat(log["end"])
            delta = end - start
            if delta.total_seconds() > 0:
                total += delta
        except (KeyError, ValueError, TypeError):
            continue
    return total

def calculate_completion_rate(user_id: str, module_ids: List[str], completion_logs: List[Dict[str, Any]]) -> float:
    """
    Calculate overall module completion rate for the user.
    
    :param user_id: User identifier
    :param module_ids: List of curriculum module IDs
    :param completion_logs: List of logs, each with {"user_id":str, "module_id":str, "completed":bool}
    :return: Fraction completed [0, 1]
    """
    if not module_ids:
        return 0.0
    completed = set(
        log["module_id"]
        for log in completion_logs
        if log.get("user_id") == user_id and log.get("completed") is True and log.get("module_id") is not None
    )
    return len(completed.intersection(module_ids)) / len(module_ids)

def analyze_performance_trends(user_id: str, performance_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze trends in student performance over time.
    
    :param user_id: User identifier
    :param performance_history: List of score/timestamp dicts
       Each entry should include: {"user_id":str, "score":float, "timestamp": ISO 8601 str}
    :return: Dict with trend summary (e.g., "improving", "declining", "stable", plus details)
    """
    # Only take this user's records and sort by timestamp
    recs = [
        d for d in performance_history
        if d.get("user_id") == user_id and isinstance(d.get("score"), (int, float)) and d.get("timestamp")
    ]
    recs.sort(key=lambda d: d["timestamp"])
    scores = [d["score"] for d in recs]
    if len(scores) < 2:
        return {"trend": "insufficient data", "details": {"scores": scores}}

    # Very simple trend: compare early vs. late mean
    first_half = scores[:len(scores)//2]
    second_half = scores[len(scores)//2:]

    mean_first = sum(first_half)/len(first_half)
    mean_second = sum(second_half)/len(second_half)

    if abs(mean_second - mean_first) < 1e-5:
        trend = "stable"
    elif mean_second > mean_first:
        trend = "improving"
    else:
        trend = "declining"
    return {
        "trend": trend,
        "details": {"first_half_mean": mean_first, "second_half_mean": mean_second, "scores": scores}
    }

def assessment_performance_analytics(user_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Summarize assessment performance for user: mean, min, max, count.
    Each record must have: {"user_id", "score"}
    """
    scores = [
        rec["score"] for rec in records
        if rec.get("user_id") == user_id and isinstance(rec.get("score"), (int, float))
    ]
    if not scores:
        return {"mean": 0.0, "min": None, "max": None, "count": 0}
    return {
        "mean": sum(scores) / len(scores),
        "min": min(scores),
        "max": max(scores),
        "count": len(scores)
    }

def engagement_score(user_id: str, interactions: List[Dict[str, Any]]) -> int:
    """
    Sum engagement points for a user by interaction type.
    - view: 1pt
    - submit_quiz: 5pt
    - post_forum: 2pt
    Unknown types: 0pt
    """
    weights = {"view": 1, "submit_quiz": 5, "post_forum": 2}
    return sum(
        weights.get(item["interaction_type"], 0) * item.get("count", 0)
        for item in interactions if item.get("user_id") == user_id
    )

def competency_mapping(user_id: str, assessments: List[Dict[str, Any]]) -> Set[str]:
    """
    Return set of competency_id values achieved by user; achieved if score >= threshold.
    Assessments: [{"user_id", "score", "competency_id", "threshold"}]
    """
    achieved = set()
    for a in assessments:
        if (
            a.get("user_id") == user_id and
            isinstance(a.get("score"), (int, float)) and
            "competency_id" in a and "threshold" in a and
            a["score"] >= a["threshold"]
        ):
            achieved.add(a["competency_id"])
    return achieved

def comparative_cohort_analytics(group1: List[Dict[str, Any]], group2: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare two cohorts by average progress/engagement.
    Each group: list of {"user_id", "progress"} dict
    cohort_higher: 1 if first is higher, 2 if second is higher, 0 if equal
    """
    def mean(group):
        vals = [g["progress"] for g in group if isinstance(g.get("progress"), (int, float))]
        return sum(vals) / len(vals) if vals else 0.0
    m1 = mean(group1)
    m2 = mean(group2)
    if abs(m1 - m2) < 1e-8:
        higher = 0
    elif m1 > m2:
        higher = 1
    else:
        higher = 2
    return {"mean_1": m1, "mean_2": m2, "cohort_higher": higher}


# In-memory storage for analytics results persistence
_analytics_storage = {}

def save_analytics_result(student_id: Any, data: dict):
    """
    Save analytics results for a student to in-memory storage.
    Used for integration testing of learning analytics.
    
    :param student_id: Student identifier
    :param data: Analytics data to store
    """
    _analytics_storage[student_id] = data

def retrieve_analytics_result(student_id: Any) -> dict:
    """
    Retrieve previously saved analytics results for a student.
    
    :param student_id: Student identifier
    :return: Stored analytics data or empty dict if not found
    """
    return _analytics_storage.get(student_id, {})

def clear_analytics_storage():
    """
    Clear all stored analytics results.
    Useful for test setup/teardown.
    """
    _analytics_storage.clear()
