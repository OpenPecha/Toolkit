from pathlib import Path

from openpecha.formatters import HFMLFormatter, TsadraFormatter
from openpecha.serializers import EpubSerializer, SerializeHFML

ebook_path = "./tests/in"
# 1. Format Tsadra Ebook to OPF (OpenPecha Format)
# 2. Serialize OPF to HFML (Human Friendly Markup Language)
# 3. Format HFML to OPF
# 4. Convert HFML to Ebook
