from pathlib import Path

from openpecha.formatters import HFMLFormatter
from openpecha.serializers import SerializeHFML

if __name__ == "__main__":
    hfml_path = "./output/hfml_test/P000001/"
    opf_path = "./output/P000001/P000001.opf/"
    pecha_id = 1

    formatter = HFMLFormatter(output_path=opf_path)
    formatter.create_opf(hfml_path, pecha_id)
