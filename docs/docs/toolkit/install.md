---
icon: material/briefcase-download-outline 
---

# Installation

Stable version:

#### `pip install openpecha`

Daily development version:

#### `pip install git+https://github.com/OpenPecha/Openpecha-Toolkit`

## Developer Installation
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
