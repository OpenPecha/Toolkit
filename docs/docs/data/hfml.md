# HFML

HFML stands for The human-friendly markup language

## Import HFML Files

Here is the hfml file [kangyur_01](https://raw.githubusercontent.com/OpenPecha-dev/openpecha-toolkit/master/tests/formatters/hfml/data/kangyur_01.txt) used in following code snippet.

```python
{!../../docs_src/importers/hfml/tutorial001.py!}
```

## Tagset

### Pagination tags

#### `[1]`

**Type:** Pagination

**Syntax:** `[<page number>]`

**Use:** Mark for modern pagination information in modern book or arabic page numbers in traditional text layout.

**Text Sample:**

![image](https://user-images.githubusercontent.com/17675331/144010744-750229ef-0e79-4952-9403-a6dc1b14f492.png)

`[360]`
`༄༅། །རྒྱ་གར་སྐད་དུ། དྷརྨ་ཙཀྲ་པྲ་བརྟ་ན་སཱུ་ཏྲ། བོད་སྐད་དུ། ཆོས་ཀྱི་འཁོར་ལོ་རབ་ཏུ་བསྐོར་བའི་མདོ། [..]`
`དྲང་སྲོང་ལྷུང་བ་རི་དགས་རྒྱུ་བའི་གནས་ན་བཞུགས་སོ། །དེ་ནས་བཅོམ་ལྡན་འདས་ཀྱིས་དགེ་སློང་ལྔ་སྡེ་རྣམས་བོས་ཏེ་བཀའ་[..]`
`དང་དམན་པར་འགྱུར་རོ། །སོ་སོའི་སྐྱེ་བོ་རྣམས་ནི་དོན་མེད་པ་དང་ལྡན་པའི་ཕྱིར་གང་སུ་དག་ལུས་དུབ་པ་དང་འབྲལ་བའི་སྡུག་[..]`  

---

#### `[1a]`

**Type:** Pecha folio pagination

**Syntax:** `[<page number><a/b side>]`

**Use:** Tag for traditional pecha page numbers spelled out in Tibetan on the front side of a folio.

**Text Sample:**

![image](https://user-images.githubusercontent.com/17675331/144010914-f86f66d9-6d41-4fd6-b271-3e8924d38ee5.png)

`[180b]`
`༄༅། །རྒྱ་གར་སྐད་དུ། དྷརྨ་ཙཀྲ་པྲ་བརྟ་ན་སཱུ་ཏྲ། བོད་སྐད་དུ། ཆོས་ཀྱི་འཁོར་ལོ་རབ་ཏུ་བསྐོར་བའི་མདོ། [..]`
`དྲང་སྲོང་ལྷུང་བ་རི་དགས་རྒྱུ་བའི་གནས་ན་བཞུགས་སོ། །དེ་ནས་བཅོམ་ལྡན་འདས་ཀྱིས་དགེ་སློང་ལྔ་སྡེ་རྣམས་བོས་ཏེ་བཀའ་[..]`
`དང་དམན་པར་འགྱུར་རོ། །སོ་སོའི་སྐྱེ་བོ་རྣམས་ནི་དོན་མེད་པ་དང་ལྡན་པའི་ཕྱིར་གང་སུ་དག་ལུས་དུབ་པ་དང་འབྲལ་བའི་སྡུག་[..]`  

[back to top](https://github.com/OpenPecha/hfml#tagset)

---

#### `[1a.1]`

**Type:** Pecha pagination

**Syntax:** `[<page number><a/b side>.<line number>]`

**Use:** Tag for line numbers in traditional pecha layout.

**Text Sample:**

![image](https://user-images.githubusercontent.com/17675331/144011119-bd4474a8-6fc3-44fa-b254-0aa2a4df228b.png)

`[180b]`
`[180b.1]༄༅། །རྒྱ་གར་སྐད་དུ། དྷརྨ་ཙཀྲ་པྲ་བརྟ་ན་སཱུ་ཏྲ། བོད་སྐད་དུ། ཆོས་ཀྱི་འཁོར་ལོ་རབ་ཏུ་བསྐོར་བའི་མདོ། [..]`
`[180b.2]དྲང་སྲོང་ལྷུང་བ་རི་དགས་རྒྱུ་བའི་གནས་ན་བཞུགས་སོ། །དེ་ནས་བཅོམ་ལྡན་འདས་ཀྱིས་དགེ་སློང་ལྔ་སྡེ་རྣམས་བོས་ཏེ་བཀའ་[..]`
`[180b.3]དང་དམན་པར་འགྱུར་རོ། །སོ་སོའི་སྐྱེ་བོ་རྣམས་ནི་དོན་མེད་པ་དང་ལྡན་པའི་ཕྱིར་གང་སུ་དག་ལུས་དུབ་པ་དང་འབྲལ་བའི་སྡུག་[..]`  

[back to top](https://github.com/OpenPecha/hfml#tagset)

---

### TOC tags

`{T###}` text ID

`{T###-##}` section/chapter ID

[back to top](https://github.com/OpenPecha/hfml#tagset)

---

---

### Footnote tags

`[^##]` inline note marker
`[^##]:` note content prefix

### Endnote tags without page reference

`(##)` endnote marker
`(##):` endnote content prefix

`[###](##):` endnote content prefix

---

### `(1)`

**Type:** Note maker

**Syntax:** `(<note number>)]`

**Use:** Marker for both footnotes and endnotes

**Text Sample:**

![image](https://user-images.githubusercontent.com/17675331/144013558-e719c85f-8158-4187-b006-44829d40d228.png)

`[517]`
`༄༅། །ཆོས་ཀྱི་འཁོར་ལོ་རབ་ཏུ་བསྐོར་བའི་མདོ།(1)`

[back to top](https://github.com/OpenPecha/hfml#tagset)

---

### `[100](1):`

**Type:** Endnote content prefix

**Syntax:** `[<page reference>](<note number>)]`

**Use:** Marker for the content of endnotes located at the end of texts.

**Text Sample:**

![](https://user-images.githubusercontent.com/17675331/144018718-802beb99-326b-4bc7-9323-bbf6fe7e2b3f.png)

`[517](1) མཚན་བྱང་འདི་ཆོས་ཚན་འདིའི་མཚན་བོད་སྐད་དུ་སྨོས་པ་[..]`
`མདོ་ཚན་བཅུ་གསུམ་སྣར་ཐང་པར་དུ་མདོ་ཨ་པའི་གཤམ་དུ་[..]`

[back to top](https://github.com/OpenPecha/hfml#tagset)

---

### Spell-checking tags

**Type:** potential error, correction suggestion

**Syntax:** `(error,suggestion)` 

**Use:** Marker for the content of endnotes located at the end of texts.

**Text Sample:**

---

### Critical aparatus

`[? ]` uncertain reading

`\<* \>` editorial restoration of lost text

`⟨* ⟩` editorial addition of omitted text

`⟪ ⟫` scribal insertion

`{ }` editorial deletion of redundant text

`{{ }}` scribal deletion

`///` textual loss at left or right edge of support

### Layout tags

| བོད། bo | ཨིན། en | རྟགས། tag | དཔེར་བརྗོད། Example |
| --- | --- | --- | --- |
| ཡིག་ཆུང་། | contains smaller text size | \<y...y> | \<yབཤད་སྒྲུབ་བསྟན་པའི་འབྱུང་གནས་དཔལ་ལྡན་བཀྲ་ཤིས་འཁྱིལ་དུ་རབ་བྱུང་བཅུ་བཞི་པའི་ལྕགས་སྤྲེལ་གྱི་ལོར་པར་དུ་བསྐྲུན་པ་དགེ་ལེགས་འཕེལ། སརྦ་མངྒ་ལཾ། །y> |
| མཛད་པ་པོ། | Name\<s> of an author, personal or corporate, of a work. | \<au....> | \<auམཛད་པ་པོ། མཁས་གྲུབ་ཀརྨ་ཆགས་མེད། གཏེར་ཆེན་ཀརྨ་གླིང་པ།> |
| དཔེ་ཆའི་མཚན་བྱང་། | contains pecha title | \<k1.......> | \<k1བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ་བཞུགས་སོ།།> |
| པོ་ཏིའི་མཚན་བྱང་། | contains poti title | \<k2.......> | \<k2༄༅། །འདུལ་བ་ཀ་བཞུགས་སོ། །> |
| ལེའུ་ཡི་མཚན་བྱང་། | contains chapter title | \<k3.......> | \<k3དཀོན་མཆོག་གསུམ་ལ་ཕྱག་འཚལ་ལོ། །> |

## Notes

*   we don't encode lines as annotations and generate them on the fly from the pagination layer and line returns in the base

## Sources

*   https://ubsicap.github.io/usfm/
*   \[gandhari.org\]\<https://gandhari.org/a_dpreface.php\>
*   \[esukhia/derge-kangyur\]\<https://github.com/Esukhia/derge-kangyur\>
*   https://www.markdownguide.org/extended-syntax/#fn:bignote

