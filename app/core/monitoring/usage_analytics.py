from typing import Optional, List, Dict, Any, DefaultDict
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass, field

@dataclass
class ActivityEvent:
    user_id: str
    event: str
    feature: str
    timestamp: int

@dataclass
class SessionRecord:
    start: int
    end: int

class UsageAnalytics:
    def __init__(self):
        self._activities: List[ActivityEvent] = []
        self._sessions: DefaultDict[str, List[SessionRecord]] = defaultdict(list)
        self._session_open: Dict[str, Optional[int]] = {}  # user_id -> last open timestamp (None if closed)
        self._lock = Lock()

    def track_activity(self, user, event: str, feature: str, timestamp: int):
        user_id = getattr(user, "user_id", str(user))
        activity = ActivityEvent(
            user_id=user_id,
            event=event,
            feature=feature,
            timestamp=timestamp
        )
        with self._lock:
            self._activities.append(activity)
            # Session handling
            if event == "session_start":
                self._session_open[user_id] = timestamp
            elif event == "session_end":
                start = self._session_open.get(user_id)
                if start is not None:
                    self._sessions[user_id].append(SessionRecord(start=start, end=timestamp))
                    self._session_open[user_id] = None

    def query_activities(self, user_id: Optional[str] = None) -> List[Dict]:
        with self._lock:
            acts = [a for a in self._activities if user_id is None or a.user_id == user_id]
            return [
                {
                    "user_id": a.user_id,
                    "event": a.event,
                    "feature": a.feature,
                    "timestamp": a.timestamp
                }
                for a in acts
            ]

    def aggregate_usage(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        # Aggregate activity and session statistics per protocol
        with self._lock:
            users = set([a.user_id for a in self._activities])
            if user_id is not None:
                users = {user_id}
            results = {
                "total_users": len(users),
                "total_sessions": 0,
                "total_activities": 0,
                "by_feature": defaultdict(int)
            }
            for user in users:
                user_acts = [a for a in self._activities if a.user_id == user]
                user_sessions = self._sessions.get(user, [])
                results["total_activities"] += len(user_acts)
                results["total_sessions"] += len(user_sessions)
                for a in user_acts:
                    results["by_feature"][a.feature] += 1
            # Convert by_feature defaultdict to regular dict
            results["by_feature"] = dict(results["by_feature"])
            return results

    def feature_usage_report(self) -> Dict[str, Dict[str, Any]]:
        """Protocol-driven report: count and (optionally) breakdown by feature."""
        with self._lock:
            feature_counts = defaultdict(int)
            for a in self._activities:
                feature_counts[a.feature] += 1
            return {f: {"count": n} for f, n in feature_counts.items()}

    def query_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            result = []
            users = [user_id] if user_id is not None else list(self._sessions.keys())
            for user in users:
                recs = self._sessions.get(user, [])
                for r in recs:
                    result.append({
                        "user_id": user,
                        "start": r.start,
                        "end": r.end,
                        "duration": r.end - r.start
                    })
            return result

    def clear(self):
        """For test cleanup: clear all activities and sessions."""
        with self._lock:
            self._activities.clear()
            self._sessions.clear()
            self._session_open.clear()

# Protocol recommends an instance (can be singletonized)
usage_analytics = UsageAnalytics()