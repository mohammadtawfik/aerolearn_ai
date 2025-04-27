# metadata_store.py

import json
import os
from typing import Dict, Any, List, Callable

class MetadataStore:
    """
    Simple file-based persistence for demonstration.
    """
    def __init__(self, db_file: str):
        self.db_file = db_file
        self._load()

    def _load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        self.index = json.loads(content)
                    else:
                        self.index = {}
            except (json.JSONDecodeError, FileNotFoundError):
                self.index = {}
        else:
            self.index = {}

    def _save(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)

    def save_metadata(self, item_id: str, metadata: Dict[str, Any]):
        self.index[item_id] = metadata
        self._save()

    def get_metadata(self, item_id: str) -> Dict[str, Any]:
        return self.index.get(item_id, {})

    def search(self, predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        return [md for md in self.index.values() if predicate(md)]

    def filter_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
        return [md for md in self.index.values() if field in md and md[field] == value]

    def list_all(self) -> List[Dict[str, Any]]:
        return list(self.index.values())