from pathlib import Path

from openpecha.formatters import TsadraFormatter
from openpecha.formatters import kangyurFormatter


def test_tsadra_formatter():
    m_text = Path('tests/data/formatter/tsadra_01.txt').read_text()
    formatter = TsadraFormatter()

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

def test_kangyur_formatter():
    m_test = Path('tests/data/formatter/kangyur_01.txt').read_text()
    formatter = kangyurFormatter()

    text = formatter.text_preprocess(m_text)
    result = formatter.build_layers(text)

    expected_result = {
        'pages': [(0, 24), (27, 676), (679, 2157)],
        'lines': [
            [(0, 24)],
            [(27, 139),(141, 267), (269, 403), (405, 540), (542, 676)],
            [(679, 870), (872, 1088), (1090, 1296), (1298, 1494), (1496, 1707), (1709, 1930), (1932, 2157)]
        ],
        'text_ids': [(27, 2157)],
        'text_sub_ids': [[(27, 1351), (1352, 1494), (1495, 2157)]]
    }

    for layer in result:
        assert result[layer] == expected_result[layer]