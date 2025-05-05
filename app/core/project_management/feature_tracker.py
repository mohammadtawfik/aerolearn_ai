from enum import Enum
from dataclasses import dataclass, field
from typing import Set, List, Dict, Optional

class FeatureStatus(Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    ON_HOLD = "ON_HOLD"
    CANCELLED = "CANCELLED"

@dataclass
class Feature:
    name: str
    component: str
    status: FeatureStatus = FeatureStatus.PLANNED
    dependencies: Set[str] = field(default_factory=set)
    status_history: List = field(default_factory=list)

class FeatureRegistry:
    def __init__(self):
        self.features: Dict[str, Feature] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}

    def register_feature(self, name, component, status="PLANNED"):
        feat = Feature(
            name=name,
            component=component,
            status=FeatureStatus[status] if isinstance(status, str) else status
        )
        self.features[name] = feat
        self.dependency_graph.setdefault(name, set())
        return feat

    def get_feature(self, name):
        return self.features.get(name)

    def update_feature_status(self, name, new_status):
        feat = self.features.get(name)
        if feat:
            old_status = feat.status
            feat.status = FeatureStatus[new_status] if isinstance(new_status, str) else new_status
            feat.status_history.append((old_status, feat.status))
            return True
        return False

    def link_feature_dependency(self, feature_name, dependency_name):
        if feature_name not in self.features or dependency_name not in self.features:
            return False
            
        self.dependency_graph.setdefault(feature_name, set()).add(dependency_name)
        self.features[feature_name].dependencies.add(dependency_name)
        return True

    def get_feature_dependency_graph(self):
        return {k: list(v) for k, v in self.dependency_graph.items()}

    def get_status_history(self, name):
        feat = self.features.get(name)
        return feat.status_history if feat else []

    def _transitive_deps(self, feature_name) -> Set[str]:
        """Return all features (names) that depend (directly or transitively) on 'feature_name'."""
        impacted = set()
        queue = [feature_name]
        while queue:
            current = queue.pop()
            for feat, deps in self.dependency_graph.items():
                if current in deps and feat not in impacted:
                    impacted.add(feat)
                    queue.append(feat)
        return impacted

    def analyze_feature_impact_from_component_change(self, component_name, component_registry):
        """
        Return all feature names that depend (directly or indirectly) on the provided component,
        according to the component registry's dependency graph.
        """
        # 1. Determine impacted components using component registry
        components_impacted = {component_name}
        components_impacted.update(component_registry.analyze_dependency_impact(component_name))
        # 2. Collect all features that have a .component in impacted
        impacted = []
        for featname, feat in self.features.items():
            if feat.component in components_impacted:
                impacted.append(featname)
        # (optional: propagate via feature-to-feature dependencies as well)
        return impacted

    def check_feature_backward_compatibility(self, feature_name, component_registry):
        """
        Check if the feature remains compatible given the versions of all the components it depends on.
        For now, this uses top-level .component field only.
        """
        feat = self.features.get(feature_name)
        if not feat:
            return False
            
        # If feature-to-feature dependencies exist, propagate check
        to_check = {feature_name}
        visited = set()
        compatible = True
        while to_check:
            cur_feat_name = to_check.pop()
            if cur_feat_name in visited:
                continue
            visited.add(cur_feat_name)
            cur_feat = self.features.get(cur_feat_name)
            if not cur_feat or not component_registry.check_version_compatibility(cur_feat.component):
                compatible = False
            # queue dependencies (fan-out to other features)
            to_check |= set(self.dependency_graph.get(cur_feat_name, []))
        return compatible

    def feature_compatibility_risk(self, feature_name, component_registry):
        """
        Get risk score for this feature due to its component(s)' compatibility risk.
        """
        feat = self.features.get(feature_name)
        if not feat:
            return 0, {}
            
        # Aggregate risk for top-level component only (could aggregate recursively in future)
        score, comp_breakdown = component_registry.calculate_compatibility_risk(feat.component)
        breakdown = {feature_name: "at risk" if score > 0 else "ok"}
        return score, breakdown
