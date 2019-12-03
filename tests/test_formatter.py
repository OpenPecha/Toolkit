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
        'page': [(0, 24,'kk'), (27, 676,'kl'), (679, 2173,'lm')],
        'topic': [(27, 2173)],
        'sub_topic': [[(27, 1351), (1352, 1494), (1495, 2173)]],
        'error': [(1838,1843,'མཆིའོ་')],
        'yigchung': [(2040,2042),(2044,2045)],
        'absolute_error':[1518,1624,1938]
    }

    for layer in result:
        print(result[layer])
        assert result[layer] == expected_result[layer]

def test_kangyur_get_base_text():
    m_text = Path('tests/data/formatter/kangyur_01.txt').read_text()
    formatter = kangyurFormatter()

    text = formatter.text_preprocess(m_text)
    formatter.build_layers(text)
    result = formatter.get_base_text()

    expected = Path('tests/data/formatter/kangyur_base.txt').read_text()

    assert result == expected