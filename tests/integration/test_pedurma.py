from pathlib import Path

from openpecha.formatters import PedurmaFormatter
from openpecha.serializers import PedurmaSerializer

if __name__ == "__main__":
    opf_path = "./output/opfs/D1111.opf/"

    serializer = PedurmaSerializer(opf_path)
    serializer.serialize()