from openpecha.formatters import HFMLFormatter

formatter_input_path = "../openpecha-user/publication/P000001-test"
formatter_output_path = "../openpecha-user/opfs"

formatter = HFMLFormatter(output_path=formatter_output_path)
formatter.create_opf(formatter_input_path)
