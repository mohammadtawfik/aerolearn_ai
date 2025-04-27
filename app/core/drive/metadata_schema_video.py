# metadata_schema.py

from typing import Any, Dict, List, Optional, Callable, Union

class MetadataField:
    def __init__(self, name: str, field_type: type, required: bool = False, default: Any = None, validator: Optional[Callable[[Any], bool]] = None, description: str = ""):
        self.name = name
        self.type = field_type
        self.required = required
        self.default = default
        self.validator = validator
        self.description = description

    def validate(self, value: Any) -> bool:
        if value is None and self.required:
            return False
        if self.validator and value is not None:
            return self.validator(value)
        return True

class MetadataSchema:
    def __init__(self, name: str, fields: List[MetadataField]):
        self.name = name
        self.fields = fields
        self.field_map = {f.name: f for f in fields}

    def validate(self, data: Dict[str, Any]) -> (bool, List[str]):
        errors = []
        for field in self.fields:
            value = data.get(field.name, field.default)
            if field.required and value is None:
                errors.append(f"{field.name} is required")
            elif value is not None and not field.validate(value):
                errors.append(f"{field.name}: invalid value '{value}'")
        return (len(errors) == 0, errors)

    def get_field(self, name: str) -> Optional[MetadataField]:
        return self.field_map.get(name)

    def get_required_fields(self) -> List[str]:
        return [f.name for f in self.fields if f.required]

    def get_optional_fields(self) -> List[str]:
        return [f.name for f in self.fields if not f.required]

# Example: Base schema with extension point
base_fields = [
    MetadataField("title", str, required=True, description="User-facing title"),
    MetadataField("author", str, required=True, description="Creator or uploader"),
    MetadataField("description", str, required=False, description="Free-form description"),
    MetadataField("tags", list, required=False, default=[], description="List of tags"),
    MetadataField("created_at", str, required=True, description="ISO date string"),
    MetadataField("updated_at", str, required=False, description="ISO date string"),
    # Extension/Custom fields supported by subclassing or dynamic extension
]

BaseMetadataSchema = MetadataSchema("BaseMetadata", fields=base_fields)

# Extension: e.g. Video metadata
video_fields = base_fields + [
    MetadataField("duration_seconds", int, required=False, description="Video duration in seconds"),
    MetadataField("format", str, required=False, description="Format, e.g. mp4"),
]

VideoMetadataSchema = MetadataSchema("VideoMetadata", fields=video_fields)