from openpecha.alignment.exporter.bitext import BitextExporter


def test_bitext():
    bitext_exporter = BitextExporter(alignment_path=None)
    segment_pair = {"P0001": "djfkdi9", "P0002": "dfdfjke7"}
    pair_id = "2345kdk354"
    segment_texts = {
        "P0001": {"2345kdk354": "རྒྱུད་གསུམ་པ།"},
        "P0002": {"2345kdk354": "The Threefold Ritual"},
    }
    expected_bitext = "རྒྱུད་གསུམ་པ།\n\tThe Threefold Ritual\n"
    bitext = bitext_exporter.serialize_segment_pair(
        pair_id, segment_pair, segment_texts
    )
    assert expected_bitext == bitext
