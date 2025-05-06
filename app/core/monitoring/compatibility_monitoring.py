from typing import Dict, Any, Callable, List, Set, Optional
from threading import Lock

class CompatibilityMonitor:
    def __init__(self):
        self._components: Dict[str, List[Dict[str, Any]]] = {}  # name -> list of registrations [{version, contract}]
        self._contract_schema: Dict[str, Dict[str, Any]] = {}  # name -> reference contract
        self._alert_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self._lock = Lock()

    def register_component(self, component):
        name = component.name
        version = getattr(component, "version", None)
        contract = getattr(component, "contract", None)
        with self._lock:
            entries = self._components.setdefault(name, [])
            entry = {"version": version, "contract": contract}
            entries.append(entry)
            # If first seen, use as baseline schema
            if name not in self._contract_schema:
                self._contract_schema[name] = dict(contract) if contract is not None else {}
            # (Optional) If multiple versions registered, check for compatibility immediately

    def validate_contract(self, name: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Validate given contract against reference schema or most recent registered version."""
        with self._lock:
            baseline = self._contract_schema.get(name, {})
            compatible, diff = self._dict_contracts_compatible(baseline, contract)
            return {"compatible": compatible, "diff": diff}

    def check_version_compatibility(self, name: str) -> Dict[str, Any]:
        """Verify if registered versions for a component are mutually compatible (no protocol policy violation)."""
        with self._lock:
            versions = [entry["version"] for entry in self._components.get(name, []) if entry["version"] is not None]
            if len(versions) <= 1:
                # Only one version => always compatible
                return {"compatible": True, "versions": versions}
            # Protocol: if versions differ, they're not compatible
            if len(set(versions)) == 1:
                return {"compatible": True, "versions": versions}
            else:
                conflict = tuple(sorted(set(versions)))
                return {"compatible": False, "versions": versions, "conflict": conflict}

    def verify_runtime_compatibility(self, name: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """At runtime, check contract against what's registered, alert if not compatible."""
        result = self.validate_contract(name, contract)
        if not result["compatible"]:
            self._trigger_alert(name, diff=result["diff"])
        return {"compatible": result["compatible"], "diff": result["diff"]}

    def on_compatibility_issue(self, callback: Callable[[Dict[str, Any]], None]):
        with self._lock:
            self._alert_handlers.append(callback)

    def _trigger_alert(self, name: str, diff: Dict[str, Any]):
        alert = {"name": name, "diff": diff}
        for handler in self._alert_handlers:
            handler(alert)

    def _dict_contracts_compatible(self, a: Dict[str, Any], b: Dict[str, Any]) -> (bool, Dict[str, Any]):
        """Return field-level diff for two contracts, True if all features/fields align as per protocol."""
        diff = {}
        keys = set(a.keys()) | set(b.keys())
        for k in keys:
            if a.get(k) != b.get(k):
                diff[k] = (a.get(k), b.get(k))
        return (not diff, diff)

    def clear(self):
        with self._lock:
            self._components.clear()
            self._contract_schema.clear()
            self._alert_handlers.clear()