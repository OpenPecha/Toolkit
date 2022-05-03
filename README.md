# OpenPecha Toolkit
[![PyPI version](https://badge.fury.io/py/openpecha.svg)](https://badge.fury.io/py/openpecha)
![Test](https://github.com/OpenPecha/openpecha-toolkit/workflows/Test/badge.svg)
![Test Coverage](https://github.com/OpenPecha/openpecha-toolkit/workflows/Test%20Coverage/badge.svg)
![Publish](https://github.com/OpenPecha/openpecha-toolkit/workflows/Publish/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

OpenPecha Toolkit allows state of the art for distributed standoff annotations on moving texts, in which Base layer can be edited without affecting annotations.

- Documentation: https://dev.openpecha.org/
- If you have any problems with `openpecha-toolkit`, please open [issues](https://github.com/OpenPecha-dev/openpecha-toolkit/issues/new/choose)


## Usage
First, we need to download all the pecha from OpenPecha.

```
$ openpecha download --help
Usage: openpecha download [OPTIONS]

  Command to download poti. You need to give a work-id of a poti to download it.

Options:
  -n, --number WORK_ID      Work-id of the poti, for single poti download
  --help                    Show this message
```

<!-- Not everything is implemented yet so shouldn't be in the README
```
$ openpecha download --help
Usage: openpecha download [OPTIONS]

  Command to download poti. If number and batch options are not provided then it
  will download all the poti.

Options:
  -n, --number WORK_ID      Work-id of the poti, for single poti download
  -b, --batch FILE          Path to a text file containg list of names of poti in separate line. Poti batch download, for multiple poti download
  -f, --filter FILTER       Filter poti by layer availability, specify layer names in comma separated, eg: title,yigchung,..
  -o, --out PATH            Directory to store all the poti (default .openpecha)
  --help                    Show this message
```
--->

Automatic updating annotations from source base-text (original) and destination base-text (edited)
```
$ openpecha update --help
Usage: openpecha update [OPTIONS] WORK_ID

  Command to update the base text with your edits.

Options:
  --help  Show this message and exit.
```

Exporting and Extracting layer
```
$ openpecha layer --help 
Usage: openpecha layer [OPTIONS] WORK_ID OUT

  Command to apply a single layer, multiple layers or all available layers
  (by default) and then export to markdown.

  Args:

      - WORK_ID is the work-id of the poti, from which given layer will be
      applied

      - OUT is the filename to the write the result. Currently support only
      Markdown file.

Options:
  -n, --name [title|tsawa|yigchung|quotes|sapche]
                                  name of a layer to be applied
  -l, --list TEXT                 list of name of layers to applied,
                                  name of layers should be comma separated
  --help                          Show this message and exit.
```




## Developer Installation.
```
$ git clone https://github.com/OpenPoti/openpecha-toolkit.git
$ cd openpecha-toolkit
$ pip install -r requirements.txt
$ pip install -e .
```

## Testing
```
$ pytest tests
```
