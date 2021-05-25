from pathlib import Path
from openpecha import formatters

from openpecha.formatters import PedurmaFormatter
from openpecha.serializers import PedurmaSerializer

if __name__ == "__main__":
    opf_path = "./output/opfs/D1111/D1111.opf/"
    opfs_path = "./output/opfs/"
    preview_path = "./output/D1111/"

    # preview to opf
    formatter = PedurmaFormatter(output_path=opfs_path)
    formatter.create_opf(preview_path)

    # OPf to diplomatic
    # serializer = PedurmaSerializer(opf_path)
    # serializer.serialize()