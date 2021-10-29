from pathlib import Path

import polib
import pytest

from openpecha.alignment.exporter.po import PoExporter


@pytest.fixture(scope="module")
def alignment_path():
    alignment_id = "b696df2dbe314e8a87881a2bc391d0d5"
    return (
        Path(__file__).parent
        / "data"
        / alignment_id
        / f"{alignment_id}.opa"
        / "Alignment.yml"
    )


@pytest.fixture(scope="module")
def bo_src_path():
    bo_src_id = "3f3fa97e02c94a3199056146b389d889"
    return Path(__file__).parent / "data" / "opfs" / bo_src_id


@pytest.fixture(scope="module")
def en_src_path():
    en_src_id = "1d154e16b23f4f9fa7c7f25cd1fd7463"
    return Path(__file__).parent / "data" / "opfs" / en_src_id


@pytest.fixture(scope="module")
def expected_bo_po_path():
    return Path(__file__).parent / "data" / "expected_bo.po"


@pytest.fixture(scope="module")
def expected_en_po_path():
    return Path(__file__).parent / "data" / "expected_en.po"


def test_po_exporter_bo(alignment_path, bo_src_path, expected_bo_po_path):
    poexporter = PoExporter(alignment_path)

    bo_src_id = bo_src_path.stem
    poexporter.file.metadata = {"Language": "bo"}
    poexporter.segment_to_entries(bo_src_id, bo_src_path, lang="bo")
    expected_bo_po = polib.pofile(expected_bo_po_path)
    for expected_entry, result_entry in zip(expected_bo_po, poexporter.file):
        assert expected_entry == result_entry
    assert expected_bo_po.metadata["Language"] == "bo"


def test_po_exporter_en(alignment_path, en_src_path, expected_en_po_path):
    poexporter = PoExporter(alignment_path)

    en_src_id = en_src_path.stem
    poexporter.file.metadata["Language"] = "en"
    poexporter.segment_to_entries(en_src_id, en_src_path, lang="en")
    expected_en_po = polib.pofile(expected_en_po_path)
    for expected_entry, result_entry in zip(expected_en_po, poexporter.file):
        assert expected_entry == result_entry
    assert expected_en_po.metadata["Language"] == "en"


def test_po_exporter_single(bo_src_path, expected_bo_po_path):
    alignment_path = Path(__file__).parent / "data" / "Single_Alignment.yml"
    poexporter = PoExporter(alignment_path)

    bo_src_id = bo_src_path.stem
    poexporter.file.metadata["Language"] = "bo"
    poexporter.segment_to_entries(bo_src_id, bo_src_path)
    expected_bo_po = polib.pofile(expected_bo_po_path)
    for expected_entry, result_entry in zip(expected_bo_po, poexporter.file):
        assert expected_entry == result_entry
    assert expected_bo_po.metadata["Language"] == "bo"
