from pathlib import Path

from openpecha.formatters import HFMLFormatter, TsadraFormatter
from openpecha.serializers import EditorSerializer, EpubSerializer, HFMLSerializer

if __name__ == "__main__":

    pecha_id = 801
    pecha_name = f"P{pecha_id:06}"
    ebook_path = f"./tests/data/serialize/tsadra/src/{pecha_name}/OEBPS/"
    opfs_path = "./tests/data/serialize/tsadra"
    opf_path = f"./tests/data/serialize/tsadra/{pecha_name}/{pecha_name}.opf/"
    hfml_path = "./output/demo/output/P000113_hfml/"
    ebook_output_path = "./tests/data/serialize/tsadra/ebook"

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
    # toc_levels = {
    #     '1': "//*[@class='tibetan-chapters']",
    #     '2': "//*[@class='tibetan-sabche1' or @class='tibetan-sabche']",
    #     '3': ""
    # }
    toc_levels = {"1": "book-number", "2": "chapter", "3": "sabche"}
    serializer = EpubSerializer(Path(opf_path))
    serializer.serialize(toc_levels, ebook_output_path)

    # Editor serializer
    # serializer = EditorSerializer(Path(opf_path))
    # serializer.serialize(ebook_output_path)
