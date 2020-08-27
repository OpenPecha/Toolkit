import os
from pathlib import Path

from openpecha.formatters import HFMLFormatter
from openpecha.serializers import HFMLSerializer

if __name__ == "__main__":
    hfml_text = "./output/hfml_test/P000002/"
    opfs_path = "./output/"
    opf_path = "./output/P000002/P000002.opf/"
    hfml_path = "./output/P000002_hfml/"
    pecha_id = 2

    # Converts HFML to OPF
    formatter = HFMLFormatter(output_path=opfs_path)
    formatter.create_opf(hfml_text, pecha_id)

    # Converts OPF to HFML
    serializer = HFMLSerializer(
        opf_path, text_id="T1", layers=["BookTitle", "Citation"]
    )
    serializer.serialize(output_path=hfml_path)
