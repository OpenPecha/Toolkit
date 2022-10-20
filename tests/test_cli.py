from pathlib import Path
from unittest import mock

from click.testing import CliRunner

import openpecha.cli


@mock.patch("openpecha.cli.download_pecha_util", autospec=True)
def test_download_pecha(mock_download_pecha_util):
    mock_download_pecha_util.return_value = Path("/tmp/P000001")
    runner = CliRunner()
    result = runner.invoke(openpecha.cli.cli, ["download-pecha", "P000001"])
    mock_download_pecha_util.assert_called_once_with(
        "P000001", out_path=None, branch=None
    )
    assert result.exit_code == 0
