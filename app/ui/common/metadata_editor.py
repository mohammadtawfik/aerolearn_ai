# metadata_editor.py

from app.core.drive.metadata_schema import MetadataSchema
from typing import Any, Dict

class MetadataEditorBase:
    def __init__(self, schema: MetadataSchema, initial_data: Dict[str, Any] = None):
        self.schema = schema
        self.data = initial_data or {}

    def set_field(self, field: str, value: Any):
        if field in self.schema.field_map:
            self.data[field] = value

    def get_metadata(self) -> Dict[str, Any]:
        return self.data

    def interactive_edit(self):
        print(f"Editing metadata for schema: {self.schema.name}")
        for field in self.schema.fields:
            current_val = self.data.get(field.name, field.default)
            prompt = f"{field.name} ({field.type.__name__}) [{'required' if field.required else 'optional'}]{f' - {field.description}' if field.description else ''}\n  Current [{current_val}]: "
            val = input(prompt)
            if val == "" and current_val is not None:
                val = current_val
            elif val == "" and field.default is not None:
                val = field.default
            elif field.type == int and val != "":
                try: val = int(val)
                except: print("Invalid input, must be integer."); continue
            elif field.type == list and val != "":
                val = [v.strip() for v in val.split(",")]
            elif field.type == str and val != "":
                val = str(val)
            self.data[field.name] = val
        valid, errors = self.schema.validate(self.data)
        if not valid:
            print("Validation errors:")
            for err in errors:
                print(f"  {err}")
            print("Please re-enter.")
            self.interactive_edit()
        return self.data