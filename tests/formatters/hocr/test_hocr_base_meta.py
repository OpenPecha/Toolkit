import tempfile
from pathlib import Path


from openpecha.utils import load_yaml, dump_yaml
from openpecha.formatters.ocr.hocr import HOCRFormatter
from test_hocr_data_provider import BDRCGBTestFileProvider

def test_google_ocr_base_meta():
    work_id = "W1KG10193"
    pecha_id = "I123456"
    
    ocr_path = Path(__file__).parent / "data" / "file_per_page" / work_id
    expected_meta_path = Path(__file__).parent / "data" / "file_per_page" / "opf_expected_datas" / "expected_hocr_meta.yml"
    buda_data_path = Path(__file__).parent / "data" / "file_per_page" / "buda_data.yml"
    ocr_import_info_path = Path(__file__).parent / "data" / "file_per_page" / "ocr_import_info.yml"
    ocr_import_info = load_yaml(ocr_import_info_path)
    buda_data = load_yaml(buda_data_path)
    bdrc_image_list_path = Path(__file__).parent / "data" / "file_per_page"
    data_provider = BDRCGBTestFileProvider(work_id, bdrc_image_list_path, buda_data, ocr_import_info, ocr_path)
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        formatter = HOCRFormatter(output_path=tmpdirname)
        pecha = formatter.create_opf(data_provider, pecha_id, {"remove_duplicate_symbols": True}, ocr_import_info)
        output_metadata = pecha.read_meta_file()
        expected_metadata = load_yaml(expected_meta_path)
        assert output_metadata["source_metadata"] == expected_metadata["source_metadata"]
        del output_metadata["ocr_import_info"]["ocr_info"]["timestamp"]
        del expected_metadata["ocr_import_info"]["ocr_info"]["timestamp"]
        del output_metadata["ocr_import_info"]["op_import_version"]
        del expected_metadata["ocr_import_info"]["op_import_version"]
        assert output_metadata["ocr_import_info"] == expected_metadata["ocr_import_info"]
        assert output_metadata["statistics"] == expected_metadata["statistics"]
        assert output_metadata["default_language"] == expected_metadata["default_language"]
        assert output_metadata["bases"] == expected_metadata["bases"]

if __name__ == "__main__":
    test_google_ocr_base_meta()