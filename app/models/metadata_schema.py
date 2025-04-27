"""
Metadata Schema and Editor

- Extensible schema for required/optional metadata fields
- Base editor UI class for dynamic metadata editing
- Enables validation, inheritance, and search
"""

from typing import List, Dict, Any, Optional

class MetadataSchemaField:
    def __init__(self, name: str, required: bool, field_type: str, description: str = ""):
        self.name = name
        self.required = required
        self.field_type = field_type
        self.description = description

class MetadataSchema:
    def __init__(self, fields: List[MetadataSchemaField]):
        self.fields = fields

    def required_fields(self):
        return [f for f in self.fields if f.required]

    def optional_fields(self):
        return [f for f in self.fields if not f.required]

    def as_dict(self):
        return {f.name: {"type": f.field_type, "required": f.required, "desc": f.description} for f in self.fields}

# UI: Barebones editor for dynamic editing (stub; real one would be in app/ui/common/metadata_editor.py and subclass QWidget)
class MetadataEditorBase:
    def __init__(self, schema: MetadataSchema):
        self.schema = schema
        self.data = {}

    def set_field(self, field: str, value: Any):
        if field in [f.name for f in self.schema.fields]:
            self.data[field] = value

    def get_metadata(self) -> Dict[str, Any]:
        return self.data