import inspect
from pathlib import Path

from openpecha.core import annotations


def get_annotation_classes():
    NON_ANNOTATION_CLASSES = ["BaseModel", "BaseAnnotation"]

    for name, obj in inspect.getmembers(annotations):
        if not inspect.isclass(obj) or name in NON_ANNOTATION_CLASSES:
            continue
        yield name, obj


def build_schema_for_annotations():
    ann_schemas_path = Path("docs_src") / "annotations"
    for ann_name, ann_class in get_annotation_classes():
        ann_schema_fn = ann_schemas_path / f"{ann_name}_schema.json"
        ann_schema_fn.write_text(ann_class.schema_json(indent=2))
        print(f"[INFO] Built {ann_name} annotation schema")


def main():
    build_schema_for_annotations()


if __name__ == "__main__":
    exit(main())
