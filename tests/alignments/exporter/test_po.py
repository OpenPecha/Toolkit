import polib

from openpecha.alignment.exporter.po import PoExporter


def test_po_exporter_bo():
    alignment_path = "./tests/data/alignment/Alignment.yml"
    poexporter = PoExporter(alignment_path)

    bo_src_id = "3f3fa97e02c94a3199056146b389d889"
    bo_src_path = f"./tests/data/alignment/opfs/{bo_src_id}"
    poexporter.segment_to_entries(bo_src_id, bo_src_path, lang="bo")
    expected_bo_po = polib.pofile("./tests/data/alignment/po/expected_bo.po")
    for expected_entry, result_entry in zip(expected_bo_po, poexporter.file):
        assert expected_entry == result_entry


def test_po_exporter_en():
    alignment_path = "./tests/data/alignment/Alignment.yml"
    poexporter = PoExporter(alignment_path)

    en_src_id = "1d154e16b23f4f9fa7c7f25cd1fd7463"
    en_src_path = f"./tests/data/alignment/opfs/{en_src_id}"
    poexporter.segment_to_entries(en_src_id, en_src_path, lang="en")
    expected_en_po = polib.pofile("./tests/data/alignment/po/expected_en.po")
    for expected_entry, result_entry in zip(expected_en_po, poexporter.file):
        assert expected_entry == result_entry
