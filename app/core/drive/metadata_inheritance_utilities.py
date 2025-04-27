# metadata_inheritance.py

from typing import Dict, Any, Optional, List

def inherit_metadata(parent_metadata: Dict[str, Any], item_metadata: Dict[str, Any], overwrite: bool = False) -> Dict[str, Any]:
    """
    For any field not present in item_metadata, inherit from parent_metadata.
    If overwrite=True, parent_metadata always replaces item_metadata.
    """
    result = item_metadata.copy()
    for k, v in parent_metadata.items():
        if overwrite or k not in result or result[k] is None:
            result[k] = v
    return result

def batch_apply_metadata(items_metadata: List[Dict[str, Any]], batch_metadata: Dict[str, Any], overwrite: bool = False) -> List[Dict[str, Any]]:
    return [inherit_metadata(batch_metadata, md, overwrite=overwrite) for md in items_metadata]