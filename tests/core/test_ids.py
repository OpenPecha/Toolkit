from openpecha.core.ids import (
    get_alignment_id,
    get_collection_id,
    get_id,
    get_pecha_id,
    get_uuid,
    get_work_id,
)


def test_get_uuid():
    assert len(get_uuid()) == 32


def test_get_id():
    random_id = get_id(prefix="S", length=6)

    assert len(random_id) == 7
    assert random_id.startswith("S")


def test_get_pecha_id():
    pecha_id = get_pecha_id()

    assert len(pecha_id) == 9
    assert pecha_id.startswith("P")


def test_get_work_id():
    work_id = get_work_id()

    assert len(work_id) == 9
    assert work_id.startswith("W")


def test_get_alignment_id():
    alignment_id = get_alignment_id()

    assert len(alignment_id) == 9
    assert alignment_id.startswith("A")


def test_get_collection_id():
    collection_id = get_collection_id()

    assert len(collection_id) == 9
    assert collection_id.startswith("C")
