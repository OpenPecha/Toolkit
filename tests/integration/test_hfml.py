import os
from pathlib import Path

from openpecha.formatters import HFMLFormatter
from openpecha.serializers import HFMLSerializer

if __name__ == "__main__":
    hfml_text = "./output/P000008_hfml/P000008"
    opfs_path = Path("./output/")
    opf_path = "./output/tengyur/P000792.opf/"
    hfml_path = "./output/tengyur/pedurma/"
    pecha_id = 1

    # Converts HFML to OPF
    # formatter = HFMLFormatter(output_path=opfs_path)
    # formatter.create_opf(hfml_text, pecha_id)

    # Converts OPF to HFML
    # text_list = Path("./output/tengyur/text_list.txt").read_text()
    # texts = text_list.splitlines()
    # for text in texts:
    serializer = HFMLSerializer(opf_path, text_id="D1118")
    serializer.serialize(output_path=hfml_path)
