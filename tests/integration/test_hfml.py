import os
from pathlib import Path

from openpecha.formatters import HFMLFormatter
from openpecha.serializers import HFMLSerializer

if __name__ == "__main__":
    hfml_text = "./output/hfml_test/P000001/"
    opfs_path = "./output/"
    opf_path = "./output/P000001/P000001.opf/"
    hfml_path = "./output/P000001_hfml/"
    pecha_id = 1

    # Converts HFML to OPF
    formatter = HFMLFormatter(output_path=opfs_path)
    formatter.create_opf(hfml_text, pecha_id)

    # Converts OPF to HFML
    serializer = HFMLSerializer(opf_path, text_id="D1")
    serializer.serialize(output_path=hfml_path)

    formatter = HFMLFormatter(output_path=opfs_path)
    formatter.create_opf(f"{hfml_path}/P000001/", 4)
