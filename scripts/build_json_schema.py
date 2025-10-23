import inspect
import json
from pathlib import Path

from pydantic import BaseModel

from openpecha.core import annotations


def get_annotation_classes():
    NON_ANNOTATION_CLASSES = ["BaseModel", "BaseAnnotation"]

    for name, obj in inspect.getmembers(annotations):
        if (
            inspect.isclass(obj)
            and name not in NON_ANNOTATION_CLASSES
            and issubclass(obj, BaseModel)
        ):
            yield name, obj


def build_schema_for_annotations():
    ann_schemas_path = Path("docs_src") / "annotations"
    for ann_name, ann_class in get_annotation_classes():
        ann_schema_fn = ann_schemas_path / f"{ann_name}_schema.json"
        schema = ann_class.model_json_schema()
        ann_schema_fn.write_text(json.dumps(schema, indent=2))
        print(f"[INFO] Built {ann_name} annotation schema")


def main():
    build_schema_for_annotations()


if __name__ == "__main__":
    exit(main())
