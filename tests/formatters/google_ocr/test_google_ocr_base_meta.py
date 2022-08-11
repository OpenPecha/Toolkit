import tempfile
from pathlib import Path

import pytest
from openpecha import config
from openpecha.utils import load_yaml
from openpecha.formatters import GoogleOCRFormatter

# TODO: by overriding self._get_image_list in the google_ocr class, it's
# possible to run this test completely offline, it would be best
@pytest.mark.skip(reason="currently depends on bdrc api")
def test_google_ocr_base_meta():
    work_id = "W24767"
    pecha_id = "I123456"
    
    ocr_path = Path(__file__).parent / "data" / work_id
    expected_meta_path = Path(__file__).parent / "data" / "expected_google_ocr_meta.yml"
    buda_data_path = Path(__file__).parent / "data" / "buda_data.yml"
    ocr_import_info_path = Path(__file__).parent / "data" / "ocr_import_info.yml"
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        buda_data = load_yaml(buda_data_path)
        ocr_import_info = load_yaml(ocr_import_info_path)
        formatter = GoogleOCRFormatter(output_path=tmpdirname)
        pecha_path = formatter.create_opf(ocr_path, pecha_id, ocr_import_info, buda_data)
        output_metadata = load_yaml(Path(f"{pecha_path}/{pecha_path.name}.opf/meta.yml"))
        expected_metadata = load_yaml(expected_meta_path)
        # this is more complex this there's a lot of random IDs generated in the process
        # so the comparison is not straightforward...
        assert output_metadata == expected_metadata

if __name__ == "__main__":
    test_google_ocr_base_meta()