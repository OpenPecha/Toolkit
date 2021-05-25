from pathlib import Path

import pytest

from openpecha.serializers import PedurmaSerializer

def test_pedurma_serializer():
    opf_path = "./tests/data/serialize/pedurma/D1111/D1111.opf/"
    expected_diplomatic_text = Path('./tests/data/serialize/pedurma/expected_diplomatic_text.txt').read_text(encoding='utf-8')
    serializer = PedurmaSerializer(opf_path)
    serializer.apply_layers()
    results = serializer.get_result()
    for vol_id, result in results.items():
        result = result.replace('::',":")
        diplomatic_text = serializer.get_diplomatic_text(result, pub='pe')
        assert expected_diplomatic_text == diplomatic_text

