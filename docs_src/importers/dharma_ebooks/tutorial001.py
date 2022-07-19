from pathlib import Path
from openpecha.formatters.dharma_ebooks import create_opf


ebook_path = Path("tests") / "formatters" / "dharma_ebooks" / "data" / "ཐེག་པ་ཆེན་པོའི་གདམས་ངག་བློ་སྦྱོང་དོན་བདུན་མ།"
output_path = Path("tests") / "formatters" / "dharma_ebooks" / "data" /"pecha"
opf_path = create_opf(ebook_path, output_path)
