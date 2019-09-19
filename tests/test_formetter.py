from pathlib import Path

from openpoti.formatter import OPFormatter

m_text = Path('data/formatter/v2.txt').read_text()

def test_build_layers():
    formatter = OPFormatter()
    
    text = formatter.text_preprocess(m_text)
    result = formatter.build_layers(text)

    expected_result = {
        'title': [0, 17],
        'yigchung': [193, 830],
        'tsawa': [919, 1073],
        'quotes': [1733, 1777],
        'sapche': [1318, 1393]
    }

    for layer, ann in expected_result.items():
        assert result[layer][0] == expected_result[layer]