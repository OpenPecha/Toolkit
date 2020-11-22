import os
from pathlib import Path

from openpecha.formatters import HFMLFormatter
from openpecha.serializers import HFMLSerializer

if __name__ == "__main__":
    hfml_text = "./output/P000008_hfml/"
    opfs_path = "./output/opfs"
    opf_path = "./output/opfs/P000008/P000008.opf/"
    hfml_path = "./output/D0001/"
    pecha_id = 8

    # Converts HFML to OPF
    # formatter = HFMLFormatter(output_path=opfs_path)
    # formatter.create_opf(hfml_text, pecha_id)

    # Converts OPF to HFML
    serializer = HFMLSerializer(opf_path, text_id="D0802")
    serializer.serialize(output_path=hfml_path)

    # formatter = HFMLFormatter(output_path=opfs_path)
    # formatter.create_opf(f"{hfml_path}/P000001/", 4)
