# OpenPecha Toolkit
[![PyPI version](https://badge.fury.io/py/openpecha.svg)](https://badge.fury.io/py/openpecha)
[![Test](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/test.yml)
[![Test Coverage](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/test-coverage.yaml/badge.svg)](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/test-coverage.yaml)
[![Publish](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/publish.yaml/badge.svg)](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/publish.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

OpenPecha Toolkit allows state of the art solution for distributed standoff annotations on moving texts, in which Base layer can be edited without affecting annotations. This is made possible by our OpenPecha Native Format called `opf` (OpenPecha Format) and our collection of `importers` which can parse existing text into `opf` and `exporters` which can export `opf` text into any format (`.epub`, `.docx`, `.pdf`, etc)

- Documentation: https://dev.openpecha.org
- If you have any problems with `openpecha-toolkit`, please open [issues](https://github.com/OpenPecha-dev/openpecha-toolkit/issues/new/choose)


## Usage



## Developer Installation.
```bash
git clone https://github.com/OpenPecha-dev/openpecha-toolkit.git
cd openpecha-toolkit
pip install -r requirements-dev.txt
pip install -e .
pre-commit install
```

## Testing
```bash
pytest tests
```
