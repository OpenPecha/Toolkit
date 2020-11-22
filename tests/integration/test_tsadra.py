from pathlib import Path

from openpecha.formatters import HFMLFormatter, TsadraFormatter
from openpecha.serializers import EpubSerializer, HFMLSerializer

if __name__ == "__main__":

    # ebook_path = "./output/demo/src/P000111/OEBPS/"
    # opfs_path = "./output/demo/output"
    # opf_path = "./output/demo/output/P000111/P000111.opf/"
    # hfml_path = "./output/demo/output/P000111_hfml/"
    # ebook_output_path = "./output/demo/output/ebooks"
    # pecha_id = 111
    # pecha_name = f"P{pecha_id:06}"

    ebook_path = "./output/demo/src/tsadra_publication/RDI-TOK-06-1/OEBPS/"
    opfs_path = "./output/demo/output"
    # opf_path = "./output/demo/output/P000101/P000101.opf/"
    opf_path = "./output/demo/output/P008259/P008259.opf/"
    hfml_path = "./output/demo/output/P000101_hfml/"
    ebook_output_path = "./output/demo/output/ebooks"
    pecha_id = 101
    pecha_name = f"P{pecha_id:06}"

    # 1. Format Tsadra Ebook to OPF (OpenPecha Format)
    # formatter = TsadraFormatter(output_path=opfs_path)
    # formatter.create_opf(ebook_path, pecha_id)

    # # 2. Serialize OPF to HFML (Human Friendly Markup Language)
    # serializer = HFMLSerializer(opf_path)
    # serializer.serialize(output_path=hfml_path)

    # # 3. Format HFML to OPF
    # formatter = HFMLFormatter(output_path=opfs_path)
    # formatter.create_opf(f"{hfml_path}/{pecha_name}", pecha_id)

    # 4. Convert OPF to Ebook
    serializer = EpubSerializer(Path(opf_path))
    serializer.apply_layers()
    serializer.serialize(ebook_output_path)
