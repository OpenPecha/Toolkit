# The OpenPecha format

The OpenPecha Format (OPF) is a standoff markdown file format in which annotation layers are linked to a base text layer. Virtually unlimited annotaton layers can be added for layers of same-type tags, witnesses, commentaries, translations, and more.

OpenPecha's Character Coordinate Translation Vector (CCTV) ties tags in annotation layers to characters in the base layer. This means that whenever a character in the base layer changes position, annotations that link to it are automatically updated to point to its new coordinates.

## On this page

<div class="grid cards" markdown>

- [:material-arrow-right-circle-outline: __File structure__](#opf-file-structure)
- [:material-arrow-right-circle-outline: __Layers__](#layers)
- [:material-arrow-right-circle-outline: __Repos and versioning__](#openpecha-data-repositories-and-versioning)

</div>

## OPF file structure
OPF is an open folder format, which means it’s not a compiled file, but simply an open folder with a specific hierarchy. An OpenPecha folder contains the following folders and files:

- A root directory with unique and persistent OpenPecha ID, e.g. **P000780** .
- An `index.yml` file that contains an index or table of contents for the text.
- A `meta.yml` file that contains metadata about the file
- A **base** folder that contains one `.txt` file for each volume in the work
- A **layers** folders that contain a `.yml` file for each annotation layer. These are linked to the base layer text. For example, **title** is a layer with formatting annotations similar to the <title></title> inline tag in HTML.

A sample OPF file might have an internal structure like this:

-    📁  P000780.opf
    - 📄 index.yml
    - 📄 meta.yml
    - 📁 base
        - v001.txt
        - v002.txt
    - 📁 layers
        - 📁 v001
            - 📄 Title.yml
            - 📄 Author.yml
            - 📄 Tsawa.yml
            - 📄 Yigchung.yml
        - 📁 v002
            - 📄 title.yml

Here is a live example [P0000001](https://github.com/OpenPecha/P000001/tree/master/P000001.opf)

## Layers

Each layer is represented by a `.yml` file and contains a collection of particular types of annotations with shared attributes.

### Types of layers

```python
class LayerEnum(Enum):
    index = "index"

    book_title = "BookTitle"
    sub_title = "SubTitle"
    book_number = "BookNumber"
    poti_title = "PotiTitle"
    author = "Author"
    chapter = "Chapter"

    topic = "Text"
    sub_topic = "SubText"

    pagination = "Pagination"
    citation = "Citation"
    correction = "Correction"
    error_candidate = "ErrorCandidate"
    peydurma = "Peydurma"
    sabche = "Sabche"
    tsawa = "Tsawa"
    yigchung = "Yigchung"
    archaic = "Archaic"
    durchen = "Durchen"
    footnote = "Footnote"
    segment = "Segment"
```

### Index layer

The index layer is similar to a table of contents and contains **text** and **subtext** annotations. The index file splits a text into subsections, and assigns to these sections unique identifiers (UUIDs). Annotation references are also stored in the index as a unique ID associated with a span of characters. Whenever there’s a change to the base text, these spans are updated. When an annotation is referred to outside the index, however, it isn’t referred to as a span (as in a tag system like XML), but as an ID.

**Example**:

```yaml
id: 68f9113d7a7f4f97b1c61af77251e6d7
annotation_type: index
revision: '00001'
annotations:
  51f58796058b461ab32f3c972ee5417c:
    work_id: T1
    parts:
      3cbe647abf404688a79c24d14742826c:
        work_id: T1-1
        span:
        - vol: 1
          start: 27
          end: 396711
    span:
    - vol: 1
      start: 27
      end: 934579
```

## Example layer

Here's the example of a **correction** layer:

```yaml
id: 2ea1861be051406a858307cd592ef5ec
annotation_type: Correction
revision: '00001'
annotations:
  1e19a11e32d54d7897021d5be594d563:
    correction: མཆིའོ་
    certainty: null
    span:
      start: 145863
      end: 145868
  497e4044c77b4877a233a3c98b267672:
    correction: མཆིའོ་
    certainty: null
    span:
      start: 145966
      end: 145971
```

## OpenPecha Data repositories and versioning

OpenPecha etexts are stored as Git repositories that include the following branches:

- Master
    - The master branch contains a `.opf` folder, which is protected
    - Only admins and repo owners can directly update the master branch from the other online branches
- Publication
    - The publication branch is for collaboratively improving the text
    - Only admin or text owners can merge changes from the publication branch to the master branch
    - GitHub Actions is set up to update the `.opf` folder in the master branch when the publication branch changes
- Custom repos
    - Here users outside of the collaboration team can edit texts and export them in various formats
    - These edits are not recorded and don't update the master branch OPF files
    - The exported text is released in the temp section of the release
- Releases
    - The **initial** section contains the src text as-is in its original format, e.g. `.txt`, `.epub`, `.hfml`, `.docx`, etc.
    - The **temp** section contains a user's exported text outside of the collaboration
    - The **V###** section contains the official release of the exported text
