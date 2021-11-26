import pytest

from openpecha.work.bdrc import get_op_work_from_bdrc_work_id, get_op_work_id


def test_get_opwork_from_bdrc_work():
    bdrc_work_id = "W987"
    op2bdrc_mapping = "op-id, bdrc-id\nW0001,W987"
    expected_work_id = "W0001"

    op_work_id = get_op_work_from_bdrc_work_id(bdrc_work_id, op2bdrc_mapping)

    assert expected_work_id == op_work_id


@pytest.mark.skip(reason="API call")
def test_get_op_work_id():
    bdrc_instance_id = "W21971"

    op_work_id = get_op_work_id(bdrc_instance_id)
