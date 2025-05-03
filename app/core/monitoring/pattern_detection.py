"""
Pattern detection, analytics integration, and learning progress trigger logic.
Implements: activity sequence analysis, resource utilization, study habit, learning style.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict


class ComponentStatus:
    """
    Represents the operational status of a monitoring component.
    """
    def __init__(self, component_name: str, is_active: bool = True, status_code: int = 200, 
                 message: str = "OK", details: Optional[Dict[str, Any]] = None):
        self.component_name = component_name
        self.is_active = is_active
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        self.timestamp = None  # Will be set when status is recorded
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert status to dictionary representation"""
        return {
            "component": self.component_name,
            "active": self.is_active,
            "status_code": self.status_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class HealthReport:
    """
    Aggregates component statuses into a comprehensive health report.
    """
    def __init__(self):
        self.components: Dict[str, ComponentStatus] = {}
        self.overall_status: str = "healthy"
        self.timestamp = None
        
    def add_component_status(self, status: ComponentStatus) -> None:
        """Add a component status to the report"""
        self.components[status.component_name] = status
        
        # Update overall status if any component is not active
        if not status.is_active:
            self.overall_status = "degraded"
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert health report to dictionary representation"""
        return {
            "overall_status": self.overall_status,
            "timestamp": self.timestamp,
            "components": {name: status.to_dict() for name, status in self.components.items()}
        }

def detect_activity_sequences(event_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze order and transitions in user learning events.
    Returns: frequent patterns, sequences found
    """
    from collections import Counter
    
    # Sort events by timestamp if available
    if event_log and 'timestamp' in event_log[0]:
        event_log = sorted(event_log, key=lambda e: e['timestamp'])
    
    # Extract activity sequences (pairs)
    sequences = []
    for i in range(len(event_log) - 1):
        current = event_log[i].get('activity', event_log[i].get('action', ''))
        next_act = event_log[i + 1].get('activity', event_log[i + 1].get('action', ''))
        sequences.append((current, next_act))
    
    # Count patterns
    pattern_counts = Counter(sequences)
    patterns = [{"from": p[0], "to": p[1], "count": c} 
                for p, c in pattern_counts.most_common()]
    
    return {
        "frequent_sequences": dict(pattern_counts)
    }

def detect_resource_utilization(event_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect overall and per-type resource usage from logs.
    Returns: summary statistics per resource
    """
    from collections import defaultdict
    
    # Track resource usage
    resources = defaultdict(int)
    
    # First, gather all resource types that appear in the log
    all_resource_types = set()
    for event in event_log:
        resource_type = event.get('resource_type')
        if resource_type:
            all_resource_types.add(resource_type)
    
    # Initialize all resource types with zero count
    for resource_type in all_resource_types:
        resources[resource_type] = 0
    
    # Count engaged resources
    for event in event_log:
        resource_type = event.get('resource_type')
        if resource_type and event.get('engaged', False):
            resources[resource_type] += 1
    
    # Convert to regular dict for return
    resource_dict = dict(resources)
    
    # Find most used resource
    most_used = None
    max_count = 0
    for resource, count in resource_dict.items():
        if count > max_count:
            max_count = count
            most_used = resource
    
    return {
        "most_used_resource": most_used,
        "usage_counts": resource_dict
    }

def infer_study_habits(event_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Identify study habit patterns (e.g., cramming, steady, random).
    Returns: inferred habit, confidence
    """
    if not event_log:
        return {"habit": "unknown", "confidence": 0.0}
    
    # Extract study sessions
    study_sessions = []
    for event in event_log:
        if 'start_time' in event and 'end_time' in event:
            study_sessions.append({
                'start_time': event['start_time'],
                'end_time': event['end_time']
            })
    
    if not study_sessions:
        return {"habit": "unknown", "confidence": 0.0}
    
    # Calculate durations
    durations = [session['end_time'] - session['start_time'] for session in study_sessions]
    avg_duration = sum(durations) / len(durations)
    
    # Determine habit type and confidence
    if len(study_sessions) == 1:
        habit = "cramming"
        confidence = 0.7
    elif avg_duration >= 45:  # Long sessions
        habit = "cramming"
        confidence = 0.8
    elif len(study_sessions) >= 3 and avg_duration < 30:  # Multiple short sessions
        habit = "steady"
        confidence = 0.9
    elif len(study_sessions) >= 2:
        habit = "steady"
        confidence = 0.6
    else:
        habit = "random"
        confidence = 0.5
    
    return {"habit": habit, "confidence": confidence}

def classify_learning_style(event_log: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Classify the learning style: e.g., 'visual', 'auditory', 'kinesthetic', 'mixed'.
    """
    from collections import Counter
    
    if not event_log:
        return {"classifier": "unknown"}
    
    # Count activity types
    activity_counts = Counter()
    for event in event_log:
        activity = event.get('activity')
        if activity:
            activity_counts[activity] += 1
    
    # No activities found
    if not activity_counts:
        return {"classifier": "unknown"}
    
    # Get the most common activity
    most_common = activity_counts.most_common()
    
    if most_common:
        top_activity, _ = most_common[0]
        
        # Map activities to learning styles
        if top_activity == "watch_video":
            return {"classifier": "visual"}
        elif top_activity == "read_content":
            return {"classifier": "reading"}
        elif top_activity == "take_quiz":
            return {"classifier": "quiz"}
    
    return {"classifier": "unknown"}


def run_pattern_detection(progress_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze raw progress records and return detected patterns (e.g., at-risk).
    
    Args:
        progress_records: List of student progress data records
        
    Returns:
        List of detected patterns with risk assessments
    """
    patterns = []
    
    for record in progress_records:
        student_id = record.get("student_id")
        if not student_id:
            continue
            
        # Simple risk detection logic
        completion_rate = record.get("completion_rate", 0)
        last_activity = record.get("last_activity_days", 0)
        
        risk = "none"
        if completion_rate < 0.3:
            risk = "high"
        elif completion_rate < 0.6:
            risk = "medium"
        elif last_activity > 14:
            risk = "medium"
            
        patterns.append({
            "student_id": student_id,
            "risk": risk,
            "factors": {
                "completion_rate": completion_rate,
                "inactivity_days": last_activity
            }
        })
    
    return patterns


def aggregate_learning_data(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate and combine learning activity data from multiple models/components.
    
    Args:
        records: Raw learning activity records
        
    Returns:
        Aggregated analytics data including breakdown by student and activity
    """
    if not records:
        return {"total_records": 0, "aggregated_data": {}, "by_student": {}, "by_activity": {}}
    
    # Extract student IDs
    student_ids = set()
    activity_types = set()
    resource_usage = {}
    by_student = {}
    by_activity_tmp = defaultdict(list)
    
    for record in records:
        student_id = record.get("student_id")
        if student_id:
            student_ids.add(student_id)
            # Group records by student_id
            if student_id not in by_student:
                by_student[student_id] = []
            by_student[student_id].append(record)
            
        activity = record.get("activity")
        if activity:
            activity_types.add(activity)
            # Group records by activity
            by_activity_tmp[str(activity)].append(record)
            
        resource = record.get("resource_id")
        if resource:
            resource_usage[resource] = resource_usage.get(resource, 0) + 1
    
    # Find most used resources
    top_resources = sorted(resource_usage.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Convert by_student dictionary keys to strings
    by_student_str_keys = {str(k): v for k, v in by_student.items()}
    
    # Format by_activity as dict of {'count': N, 'records': [...]}
    by_activity = {
        k: {"count": len(v), "records": v}
        for k, v in by_activity_tmp.items()
    }
    
    return {
        "total_records": len(records),
        "unique_students": len(student_ids),
        "activity_types": list(activity_types),
        "top_resources": dict(top_resources),
        "by_student": by_student_str_keys,
        "by_activity": by_activity
    }


def should_trigger_intervention(analytics: Dict[str, Any]) -> bool:
    """
    Decide if intervention should be triggered based on analytics.
    
    Args:
        analytics: Aggregated analytics data including patterns
        
    Returns:
        Boolean indicating if intervention is needed
    """
    # Check for high-risk patterns
    patterns = analytics.get("patterns", [])
    high_risk_count = sum(1 for p in patterns if p.get("risk") == "high")
    
    # Trigger if any high risk students or too many medium risk
    medium_risk_count = sum(1 for p in patterns if p.get("risk") == "medium")
    
    return high_risk_count > 0 or medium_risk_count >= 3


def get_intervention_recommendations(student_id: str, analytics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate personalized intervention recommendations for a specific student.
    
    Args:
        student_id: The ID of the student
        analytics: Aggregated analytics data
        
    Returns:
        Intervention recommendations or None if not needed
    """
    # Find student's pattern data
    student_data = None
    for pattern in analytics.get("patterns", []):
        if pattern.get("student_id") == student_id:
            student_data = pattern
            break
            
    if not student_data or student_data.get("risk") == "none":
        return None
        
    # Generate recommendations based on risk factors
    recommendations = []
    factors = student_data.get("factors", {})
    
    if factors.get("completion_rate", 1.0) < 0.5:
        recommendations.append({
            "type": "content_review",
            "message": "Review incomplete course materials",
            "priority": "high"
        })
        
    if factors.get("inactivity_days", 0) > 7:
        recommendations.append({
            "type": "engagement",
            "message": "Re-engage with course activities",
            "priority": "medium"
        })
    
    return {
        "student_id": student_id,
        "risk_level": student_data.get("risk"),
        "recommendations": recommendations
    }
