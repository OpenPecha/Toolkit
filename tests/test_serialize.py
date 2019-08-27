from openpoti.serializemd import SerializeMd

op_path = 'usage/layer_output'
test_op = 'W1OP000001'
test_opf_path = f'{op_path}/{test_op}/{test_op}.opf'


def test_readbaselayer():
    smd = SerializeMd(test_opf_path)
    assert isinstance(smd.baselayer, str)