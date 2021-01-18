import re
import shutil
from pathlib import Path

import pytest
import yaml

from openpecha.blupdate import Blupdate, PechaBaseUpdate


@pytest.fixture(params=[{"srcbl": "abefghijkl", "dstbl": "abcdefgkl"}])
def inputs(request):
    return request.param


@pytest.fixture(params=[{"expected_result": [(0, 2, 0), (2, 5, 2), (8, 10, -1)]}])
def compute_cctv_test_cases(request):
    return request.param


def test_compute_cctv(inputs, compute_cctv_test_cases):
    updater = Blupdate(inputs["srcbl"], inputs["dstbl"])

    result = updater.cctv

    assert result == compute_cctv_test_cases["expected_result"]


@pytest.fixture(
    params=[
        {"srcblcoord": 3, "expected_result": (2, True)},
        {"srcblcoord": 7, "expected_result": (1, False)},
        {"srcblcoord": 9, "expected_result": (-1, True)},
        {"srcblcoord": 5, "expected_result": (1, False)},
    ]
)
def cctv_for_coord_test_cases(request):
    return request.param


def test_get_cctv_for_coord(inputs, cctv_for_coord_test_cases):
    updater = Blupdate(inputs["srcbl"], inputs["dstbl"])

    result = updater.get_cctv_for_coord(cctv_for_coord_test_cases["srcblcoord"])

    assert result == cctv_for_coord_test_cases["expected_result"]


@pytest.fixture(
    params=[
        {"srcblcoord": 3, "expected_result": ("abe", "fghi")},
        {"srcblcoord": 7, "expected_result": ("fghi", "jkl")},
    ]
)
def get_context_test_cases(request):
    return request.param


def test_get_context(inputs, get_context_test_cases):
    updater = Blupdate(inputs["srcbl"], inputs["dstbl"], context_len=4)

    result = updater.get_context(get_context_test_cases["srcblcoord"])

    assert result == get_context_test_cases["expected_result"]


@pytest.fixture(
    params=[
        {"context": ("fghi", "jkl"), "dstcoordestimate": 8, "expected_result": 7},
        {"context": ("ab", "efgh"), "dstcoordestimate": 4, "expected_result": 4},
        {"context": ("ghij", "kl"), "dstcoordestimate": 7, "expected_result": 7},
    ]
)
def dmp_find_test_cases(request):
    return request.param


def test_dmp_find(inputs, dmp_find_test_cases):
    updater = Blupdate(inputs["srcbl"], inputs["dstbl"], context_len=4)

    result = updater.dmp_find(
        dmp_find_test_cases["context"], dmp_find_test_cases["dstcoordestimate"]
    )

    assert result == dmp_find_test_cases["expected_result"]


@pytest.fixture(
    params=[
        {"srcblcoord": 0, "expected_result": 0},
        {"srcblcoord": 2, "expected_result": 4},
        {"srcblcoord": 7, "expected_result": 7},
    ]
)
def updated_coord(request):
    return request.param


def test_updated_coord(inputs, updated_coord):
    updater = Blupdate(inputs["srcbl"], inputs["dstbl"], context_len=4)

    result = updater.get_updated_coord(updated_coord["srcblcoord"])

    assert result == updated_coord["expected_result"]


# Test on real text
data_path = Path("tests/data/blupdate")


@pytest.fixture(scope="module")
def updater():
    srcbl = (data_path / "v1" / "v1.opf" / "base.txt").read_text()
    dstbl = (data_path / "v2" / "v2.opf" / "base.txt").read_text()
    updater = Blupdate(srcbl, dstbl)
    return updater


def get_layer(layer_name, result, expected):
    src_layer = (
        data_path / result / f"{result}.opf" / "layers" / "v001" / f"{layer_name}.yml"
    )
    dst_layer = (
        data_path
        / expected
        / f"{expected}.opf"
        / "layers"
        / "v001"
        / f"{layer_name}.yml"
    )
    return yaml.safe_load(src_layer.open()), yaml.safe_load(dst_layer.open())


def is_layer_same(result_layer, expected_layer):
    for ann_id, result_ann in result_layer["annotations"].items():
        expected_span = expected_layer["annotations"][ann_id]["span"]
        if (
            expected_span["start"] != result_ann["span"]["start"]
            or expected_span["end"] != result_ann["span"]["end"]
        ):
            return False
    return True


def test_update():
    src_opf_path = data_path / "v1" / "v1.opf"
    dst_opf_path = data_path / "v1_base_edited" / "v1_base_edited.opf"
    expected_opf_path = data_path / "v2" / "v2.opf"

    # edit v1 base
    dst_opf_path.mkdir(exist_ok=True, parents=True)
    shutil.copytree(str(src_opf_path / "layers"), str(dst_opf_path / "layers"))
    shutil.copytree(str(expected_opf_path / "base"), str(dst_opf_path / "base"))

    pecha = PechaBaseUpdate(src_opf_path, dst_opf_path)
    pecha.update()

    for layer in ["title", "yigchung", "quotes", "tsawa", "sapche"]:
        result_layer, expected_layer = get_layer(layer, "v1_base_edited", "v2")
        assert is_layer_same(result_layer, expected_layer)

    shutil.rmtree(str(dst_opf_path.parent))
