from pathlib import Path

from openpecha.formatters import HFMLFormatter

hfml_fn = Path("tests") / "formatters" / "hfml" / "data" / "kangyur_01.txt"
m_text = hfml_fn.read_text(encoding='utf-8')

formatter = HFMLFormatter()

text = formatter.text_preprocess(m_text)
formatter.build_layers(text, len([text]))
result = formatter.get_base_text()
