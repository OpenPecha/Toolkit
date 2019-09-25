# OpenPoti Toolkit

OpenPoti Toolkit allows state of the art for distributed standoff annotations on moving texts, in which Base layer can be edited without affecting annotations. 

The motivation for this project it that for perfect base-text, there no big obstacles but the technical problems come in when you have to be able to edit the base-text, which can be correcting or updating the base-text. So the existing solution like using character coordinates won’t work. So we purposed the CCTV (Character Coordinate Translation Vector) to track the annotations from source base-text to edited base-text without worrying about the annotations at all. Then user can export the edited based text with updated annotations in various docuemnt format like `.md`, `.epub`, `.pdf`, etc. But currently it supports only markdown file.

For NLP this toolkit will provide a way to have annoated corpra with minimal errors and extract a particular type of annotation or collection of different type of annotations. NLP researchers can then use these corpus to build language model, annotations to build NER model, entity linking, ect.

## Installation
```
$ pip install openpoti
```

## Usage
Frist we need to download all the poti which are in openpoti format.
```
$ openpoti download <save_path>
```

Automatic updating annotations from source base-text (original) and destination base-text (edited)
```
$ openpoti update <source_base-text_path> <destination_base-text_path>
```

Exporting and Extracting layer
```
$ openpoti layer --help 
Usage: openpoti layer [OPTIONS] OPF_PATH OUT

  Command to apply a single layer, multiple layers or all available layers (by default) and then export to markdown.

  Args:
      - OPF_PATH is the path to opf directory of poti
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
$ git clone https://github.com/OpenPoti/openpoti-toolkit.git
$ cd openpoti-toolkit
$ pip install -e .
```

## Testing
```
$ cd tests
$ pytest
```
