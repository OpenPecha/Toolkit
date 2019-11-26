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
    m_text = Path('tests/data/formatter/kangyur_01.txt').read_text()
    formatter = kangyurFormatter()

    text = formatter.text_preprocess(m_text)
    result = formatter.build_layers(text)

    expected_result = {
        'page': [(0, 24), (27, 676), (679, 2173)],
        'line': [
            [(0, 24)],
            [(27, 139),(141, 267), (269, 403), (405, 540), (542, 676)],
            [(679, 870), (872, 1088), (1090, 1296), (1298, 1494), (1496, 1707), (1709, 1936), (1938, 2173)]
        ],
        'text': [(27, 2173)],
        'sub_text': [[(27, 1351), (1352, 1494), (1495, 2173)]],
        'error': [(1838,1843,'མཆིའོ་')],
        'yigchung': [(2040,2042),(2044,2045)],
        'unreadable':[1518,1624,1938]
    }

    for layer in result:
        print(result[layer])
        assert result[layer] == expected_result[layer]