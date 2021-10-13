from pathlib import Path

from openpecha.alignment.exporter.po import PoExporter


def test_po_exporter_bo():
    alignment_path = "./tests/data/alignment/Alignment.yml"
    poexporter = PoExporter(alignment_path)

    output_file = "./tests/data/alignment/bo.po"
    bo_src_id = "CJKBO001"
    bo_src_path = "./tests/data/alignment/CJKBO001"
    poexporter.segment_to_entries(bo_src_id, bo_src_path, lang="bo")
    poexporter.write_to_file(output_file)


def test_po_exporter_en():
    alignment_path = "./tests/data/alignment/Alignment.yml"
    poexporter = PoExporter(alignment_path)

    output_file = "./tests/data/alignment/en.po"
    en_src_id = "CJKEN001"
    en_src_path = "./tests/data/alignment/CJKEN001"
    poexporter.segment_to_entries(en_src_id, en_src_path, lang="en")
    poexporter.write_to_file(output_file)
