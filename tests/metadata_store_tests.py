# test_metadata_store.py

import os
import tempfile
from app.core.drive.metadata_store import MetadataStore

def test_metadata_store_basic():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        path = tmp.name
    try:
        store = MetadataStore(path)
        item_id = "item1"
        data = {"title": "Airfoil Data", "author": "Ada", "created_at": "2024-06-08"}
        store.save_metadata(item_id, data)
        assert store.get_metadata(item_id) == data
        # Overwrite
        new_data = {"title": "Airfoil X", "author": "Bob", "created_at": "2024-06-08"}
        store.save_metadata(item_id, new_data)
        assert store.get_metadata(item_id) == new_data
        # Search
        store.save_metadata("item2", {"title": "Prop Data", "author": "Ada", "created_at": "2024-06-08"})
        results = store.filter_by_field("author", "Ada")
        assert len(results) == 1 or len(results) == 2  # if both Ada
    finally:
        if os.path.exists(path):
            os.remove(path)