import os
from pathlib import Path

from openpecha.formatters import HFMLFormatter
from openpecha.serializers import HFMLSerializer

if __name__ == "__main__":
    hfml_text = "./tests/data/formatter/hfml/P000002/"
    opfs_path = Path("./output/opfs")
    opf_path = "./tests/data/serialize/hfml/P000002.opf/"
    hfml_path = "./output/"
    pecha_id = "P000002"

    # Converts HFML to OPF
    # formatter = HFMLFormatter(output_path=opfs_path)
    # formatter.create_opf(hfml_text, pecha_id)

    # Converts OPF to HFML
    # text_list = Path("./output/tengyur/text_list.txt").read_text()
    # texts = text_list.splitlines()
    # for text in texts:
    serializer = HFMLSerializer(opf_path)
    serializer.serialize(output_path=hfml_path)
