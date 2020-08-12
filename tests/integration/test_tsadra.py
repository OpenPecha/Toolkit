from pathlib import Path

from openpecha.formatters import HFMLFormatter, TsadraFormatter
from openpecha.serializers import EpubSerializer, SerializeHFML

ebook_path = "./output/P000101/OEBPS/"
opf_path = "./output/P000100/P000100.opf/"
hfml_path = "./output/P000100_hfml/"
pecha_id = 100


# 1. Format Tsadra Ebook to OPF (OpenPecha Format)
formatter = TsadraFormatter()
formatter.create_opf(ebook_path, pecha_id)


# 2. Serialize OPF to HFML (Human Friendly Markup Language)
serializer = SerializeHFML(opf_path)
serializer.apply_layers()
results = serializer.get_result()
for vol_id, hfml_text in results.items():
    Path(f"./output/P000100_hfml/{vol_id}.txt").write_text(hfml_text)


# 3. Format HFML to OPF
formatter = HFMLFormatter()
formatter.create_opf(hfml_path, pecha_id)


# 4. Convert OPF to Ebook
serializer = EpubSerializer(Path(opf_path))
serializer.apply_layers()
serializer.serilize(pecha_id)
