class UsageAnalytics:
    """
    Protocol-compliant UsageAnalytics implementation.
    Implements:
        - track_activity(user_id, event, feature, timestamp)
        - query_activities(user_id=None)
        - aggregate_usage(user_id=None)
        - feature_usage_report()
        - query_sessions(user_id=None)
        - clear()
    Docs: /docs/architecture/health_monitoring_protocol.md
    """

    def __init__(self):
        self._activities = []
        self._sessions = []

    def track_activity(self, user_id, event, feature, timestamp):
        """
        Records an activity (user interaction).
        Docs: /docs/architecture/health_monitoring_protocol.md
        """
        entry = {
            "user_id": user_id,
            "event": event,
            "feature": feature,
            "timestamp": timestamp
        }
        self._activities.append(entry)

    def query_activities(self, user_id=None):
        """
        Returns protocol-compliant list of activity dicts
        - Fields: user_id, event, feature, timestamp
        - Optional filter by user_id
        """
        if user_id:
            return [a for a in self._activities if a["user_id"] == user_id]
        return list(self._activities)
        
    def aggregate_usage(self, user_id=None):
        """
        Aggregates usage by user and/or system, as specified by
        /docs/architecture/health_monitoring_protocol.md and TDD test.
        Returns a dict with:
          - per-user: total_events (count of activity events)
          - per-user: features (dict with counts per feature)
        """
        from collections import defaultdict

        def summarize(activities):
            total_events = len(activities)
            features = defaultdict(int)
            for act in activities:
                features[act["feature"]] += 1
            # Return summary with protocol-compliant fields only
            return {
                "total_events": total_events,
                "features": dict(features)
            }

        # user_id specified: return one summary
        if user_id is not None:
            activities = [a for a in self._activities if a["user_id"] == user_id]
            return summarize(activities)
        # All users: build dict keyed by user_id
        by_user = defaultdict(list)
        for act in self._activities:
            by_user[act["user_id"]].append(act)
        agg = {uid: summarize(alist) for uid, alist in by_user.items()}
        return agg

    def feature_usage_report(self):
        """
        Protocol: Returns Dict[feature, count] system-wide.
        """
        from collections import defaultdict
        features = defaultdict(int)
        for act in self._activities:
            features[act["feature"]] += 1
        return dict(features)

    def query_sessions(self, user_id=None):
        """
        Returns all session records, or only those matching user_id,
        with protocol-documented fields: user_id, start, end, duration.
        """
        if user_id is not None:
            return [s for s in self._sessions if s["user_id"] == user_id]
        return list(self._sessions)

    def clear(self):
        """
        Clears all tracked activities and sessions.
        """
        self._activities.clear()
        self._sessions.clear()
