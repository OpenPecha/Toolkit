<h1 align="center">
  <br>
  <a href="https://openpecha.org"><img src="https://avatars.githubusercontent.com/u/82142807?s=400&u=19e108a15566f3a1449bafb03b8dd706a72aebcd&v=4" alt="OpenPecha" width="150"></a>
  <br>
</h1>

<h3 align="center">OpenPecha Toolkit</h3>

<!-- Replace the title of the repository -->

<p align="center">
  <a href="#description">Description</a> •
  <a href="#owner">Owner</a> •
  <a href="#floppy_disk-install">Install</a> •
  <a href="#docs">Docs</a>
</p>
<hr>

## Description

[![PyPI version](https://badge.fury.io/py/openpecha.svg)](https://badge.fury.io/py/openpecha)
[![Test](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/test.yml)
[![Test Coverage](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/test-coverage.yaml/badge.svg)](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/test-coverage.yaml)
[![Publish](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/publish.yaml/badge.svg)](https://github.com/OpenPecha-dev/openpecha-toolkit/actions/workflows/publish.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

OpenPecha Toolkit allows state of the art solution for distributed standoff annotations on moving texts, in which Base layer can be edited without affecting annotations. This is made possible by our OpenPecha Native Format called `opf` (OpenPecha Format) and our collection of `importers` which can parse existing text into `opf` and `exporters` which can export `opf` text into any format (`.epub`, `.docx`, `.pdf`, etc)

<!-- This section provides a high-level overview for the repo -->

## Owner

- [@10zinten](https://github.com/10zinten)

<!-- This section lists the owners of the repo -->


## :floppy_disk: Install
Stable version:

#### `pip install openpecha`

Daily development version:

#### `pip install git+https://github.com/OpenPecha/Openpecha-Toolkit`


<!-- This section must list as bulleted list how this repo depends or is integrated with other repos -->

## Docs

- Documentation: [docs](https://docs.openpecha.org)
- If you have any problems with `openpecha-toolkit`, please open [issues](https://github.com/OpenPecha-dev/openpecha-toolkit/issues/new/choose)

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
PYTHONPATH=.:$PYTHONPATH pytest tests
```
<!-- This section must link to the docs which are in the root of the repository in /docs -->
