# OPF Format

Versioning

OPF file structure
Layers
Types of layers
Index layer



## OpenPecha Repositories

OpenPecha etexts are stored as Git repositories that include the following branches:

- Master
    - The master branch contains the .opf, which is protected
    - Only admins and repo owners can directly update the master branch from the other online branches
- Publication
    - The publication branch is for collaboratively improving the text
    - Only admin or text owners can merge changes from the publication branch to the master branch
    - GitHub Actions is set up to update the .opf in the master branch when the publication branch changes
- Custom repos
    - Here users outside of the collaboration team can edit texts and export them in various formats
    - These edits are not recorded and don't update the master branch OPF files
    - The exported text is released in the **temp** section of the release
- Releases
    - Initial section contains the src text as-is—they may be plain text, ebook, HFML, word, etc.
    - Temp section contains the exported text of the user outside of the collaboration
    - V### section contains the official release of the exported text

## OPF Files
OPF is an open folder format, which means it’s not a compiled file, but simply an open folder with a specific hierarchy. An OpenPecha folder contains the following folders and files:

- A root directory with unique and persistent OpenPecha ID **P000780** 
- An `index.yml` file that contains an index or table of contents for the text. - The key to the format is the **index**. The index splits a text into subsections, and gives these sections unique identifiers (UUIDs). These logical units, for convenience’s sake, use the source document’s splits. Any annotation reference is also then stored in the index as a unique ID associated with a span of characters. Whenever there’s a change to the base text, these spans are updated. When an annotation is referred to outside the index, however, it isn’t referred to as a span (as it is in a tag system like XML, for example), but as an ID.
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

Layers are represented by a YAML file. They are a collection of particular types of [annotations](annotations.md) with some attributes. Here is the example of a **correction** layer:

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

## Types of layers

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

The index layer is similar to a **table of contents** and contains **text** and **subtext** annotations.

here is an example of index layer.
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

Here is a live example of [P000001](https://github.com/OpenPecha/P000001/blob/master/P000001.opf/index.yml)
