import os
from pathlib import Path

from openpecha.formatters import HFMLFormatter
from openpecha.serializers import SerializeHFML

if __name__ == "__main__":
    hfml_text = "./output/hfml_test/P000002/"
    opfs_path = "./output/"
    opf_path = "./output/P000002/P000002.opf/"
    hfml_path = "./output/P000002_hfml/"
    pecha_id = 2

    formatter = HFMLFormatter(output_path=opfs_path)
    formatter.create_opf(hfml_text, pecha_id)

    serializer = SerializeHFML(opf_path)
    serializer.apply_layers()
    results = serializer.get_result()
    for vol_id, hfml_text in results.items():
        Path(f"{hfml_path}/{vol_id}.txt").write_text(hfml_text)
    # os.system(f"rm -r {opf_path}")
