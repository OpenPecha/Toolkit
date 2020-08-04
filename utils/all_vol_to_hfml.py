from pathlib import Path

from openpecha.serializers import SerializeHFML


def serialize_vol(opf_path, vol_id, out_path):
    serializer = SerializeHFML(opf_path, vol_id=vol_id)
    serializer.apply_layers()

    result = serializer.get_result()
    out_fn = out_path / f"{vol_id}.txt"
    out_fn.write_text(result)


if __name__ == "__main__":
    data_path = Path("../openpecha-user")
    opf_path = data_path / ".openpecha/data/P000005/P000005.opf"
    out_path = data_path / "text"
    out_path.mkdir(exist_ok=True, parents=True)

    for fn in (opf_path / "base").iterdir():
        # if not fn.stem == 'v014': continue
        print(f"[INFO] Processing {fn.stem} ....")
        serialize_vol(opf_path, fn.stem, out_path)
