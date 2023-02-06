# HFML - the human-friendly markup language

Simple markup language for semantic annotations.

## Tagset

[**Pagination tags**](https://github.com/OpenPecha/hfml#pagination-tags)

*   [`[1]`](https://github.com/OpenPecha/hfml#1)
*   [`[1a]`](https://github.com/OpenPecha/hfml#1a)
*   [`[1a.1]`](https://github.com/OpenPecha/hfml#1a1)

[**Footnote tags**](https://github.com/OpenPecha/hfml#footnote-tags)

*   [`(1)`](https://github.com/OpenPecha/hfml#1-1)
*   [`[100](1)`](https://github.com/OpenPecha/hfml#1001)

## Pagination tags

### `[1]`

**Type:** Pagination

**Syntax:** `[<page number>]`

**Use:** Mark for modern pagination information in modern book or arabic page numbers in traditional text layout.

**Text Sample:**

![image](https://user-images.githubusercontent.com/17675331/144010744-750229ef-0e79-4952-9403-a6dc1b14f492.png)

`[360]`  
`༄༅། །རྒྱ་གར་སྐད་དུ། དྷརྨ་ཙཀྲ་པྲ་བརྟ་ན་སཱུ་ཏྲ། བོད་སྐད་དུ། ཆོས་ཀྱི་འཁོར་ལོ་རབ་ཏུ་བསྐོར་བའི་མདོ། [..]`  
`དྲང་སྲོང་ལྷུང་བ་རི་དགས་རྒྱུ་བའི་གནས་ན་བཞུགས་སོ། །དེ་ནས་བཅོམ་ལྡན་འདས་ཀྱིས་དགེ་སློང་ལྔ་སྡེ་རྣམས་བོས་ཏེ་བཀའ་[..]`  
`དང་དམན་པར་འགྱུར་རོ། །སོ་སོའི་སྐྱེ་བོ་རྣམས་ནི་དོན་མེད་པ་དང་ལྡན་པའི་ཕྱིར་གང་སུ་དག་ལུས་དུབ་པ་དང་འབྲལ་བའི་སྡུག་[..]`  

[back to top](https://github.com/OpenPecha/hfml#tagset)

---

### `[1a]`

**Type:** Pecha pagination

**Syntax:** `[<folio number><a/b side>]`

**Use:** Tag for traditional pecha page numbers spelled out in Tibetan on the front side of a folio.

**Text Sample:**

![image](https://user-images.githubusercontent.com/17675331/144010914-f86f66d9-6d41-4fd6-b271-3e8924d38ee5.png)

`[180b]`  
`༄༅། །རྒྱ་གར་སྐད་དུ། དྷརྨ་ཙཀྲ་པྲ་བརྟ་ན་སཱུ་ཏྲ། བོད་སྐད་དུ། ཆོས་ཀྱི་འཁོར་ལོ་རབ་ཏུ་བསྐོར་བའི་མདོ། [..]`  
`དྲང་སྲོང་ལྷུང་བ་རི་དགས་རྒྱུ་བའི་གནས་ན་བཞུགས་སོ། །དེ་ནས་བཅོམ་ལྡན་འདས་ཀྱིས་དགེ་སློང་ལྔ་སྡེ་རྣམས་བོས་ཏེ་བཀའ་[..]`  
`དང་དམན་པར་འགྱུར་རོ། །སོ་སོའི་སྐྱེ་བོ་རྣམས་ནི་དོན་མེད་པ་དང་ལྡན་པའི་ཕྱིར་གང་སུ་དག་ལུས་དུབ་པ་དང་འབྲལ་བའི་སྡུག་[..]`  

[back to top](https://github.com/OpenPecha/hfml#tagset)

---

### `[1a.1]`

**Type:** Pecha pagination

**Syntax:** `[<folio number><side>.<line>]`

**Use:** Tag for line numbers in traditional pecha layout. The sides are note a/b or ན/བ

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


## Reference

<details>
  <summary>HFML tagset from 2021</summary>
  
  # HFML - the human-friendly markup language

Simple markup language for semantic annotations.

## HFML Tags

### IE tags

| བོད། bo           | ཨིན། en                       | རྟགས། tag        | དཔེར་བརྗོད། Example                                                                                           |
|------------------|------------------------------|-----------------|------------------------------------------------------------------------------------------------------------|
| མཚོན་བྱ།           | what is defined              | <a.......>      | <aཤེས་བྱ>                                                                                                    |
| མཚན་ཉིད།          | definition                   | <b.......>      | <bབློའི་ཡུལ་དུ་བྱ་རུང་>                                                                                           |
| མཚན་གཞི།          | instance                     | <c.......>      |                                                                                                            |
| དབྱེ་གཞི།           | what is enumerated           | <d.......>      | <dསྒྲ་ལ་བརྗོད་བྱེད་ཀྱི་སྒྲའི་སྒོས་>དབྱེ་ན་གཉིས་ཡོད་དེ།                                                                       |
| དབྱེ་བ།            | enumeration                  | <e.......>      | <eསེམས་ཅན་ལ་སྟོན་པའི་སྒྲ་དང་། སེམས་ཅན་ལ་མི་སྟོན་པའི་སྒྲ་>གཉིས་ཡོད་པའི་ཕྱིར།                                                  |
| སྒྲ་བཤད།           | word part explanation        | <f.......>      |                                                                                                            |
| སྒྲ་གཞི།            | what is explained            | <l.......>      |                                                                                                            |
| ལུང་ཚིག            | citation                     | <g.......g>     | <gའགྲོ་ལ་ཕན་པར་བྱེད་རྣམས་ལམ་ཤེས་ཉིད་ཀྱིས་འཇིག་རྟེན་དོན་སྒྲུབ་མཛད་པ་གང་g>ཞེས་གསུངས་པ་ཡིན་པའི་ཕྱིར།                                |
| ལུང་ཁུངས།          | source                       | <h.......>      | <hམངོན་རྟོགས་རྒྱན་ལས།>                                                                                          |
| མཛད་བྱང་།         | colophon                     | <i.......>      | <iབཤད་སྒྲུབ་བསྟན་པའི་འབྱུང་གནས་དཔལ་ལྡན་བཀྲ་ཤིས་འཁྱིལ་དུ་རབ་བྱུང་བཅུ་བཞི་པའི་ལྕགས་སྤྲེལ་གྱི་ལོར་པར་དུ་བསྐྲུན་པ་དགེ་ལེགས་འཕེལ། སརྦ་མངྒ་ལཾ། །>   |
| བསྒྱུར་བྱང་།         | translation statement        | <j.......>      |                                                                                                            |
| གོ་བྱ།             | what is explained            | <n........>     |                                                                                                            |
| གོ་དོན།            | meaning                      | <n*........>    |                                                                                                            |
| དཔེར་བརྗོད།         | example                      | <n**........>   |                                                                                                            |
| འགྲེལ་གཞི།          | what is explained            | <o..........>   | <oདལ་བ་>ཞེས་བྱ་བ་ནི་                                                                                          |
| འགྲེལ་བཤད།         | emplanation                  | <o*..........>  | <oརི་བོ་>ནི་<o*ས་འཛིན་ནོ། །>                                                                                    |
| སྐབས་བསྟུན་འགྲེལ་བཤད། | context-specific explanation | <o**..........> | <o** མི་ཁོམ་པ་ལས་ལོག་པ་སྟེ། འདིར་ནི་སྡོམ་པ་འཆགས་པ་ལ་དལ་བ་ཞེས་བྱའོ། །>                                                  |
| འཇུག་ཡུལ།          | agreement female             | <p........>     | <pཐ་སྙད་ཀྱི་དབང་དུ་བྱས་པ་གསུམ་ལ་འཇུག་ཅིང་། དངོས་པོའ་ིདབང་གིས་བཞི་རུ་འཇུག་པར་འགྱུར་ལ། དུས་ཀྱི་དབང་གིས་གཉིས་ལ་འཇུག་པ་>ཡིན་པའི་ཕྱིར་རོ། ། |
| འཇུག་བྱ།           | agreement male               | <p*........>    | <p*དེ་ཞེས་གྲུབ་པ་དེ་ནི། དོན་དགུ་ལ་འཇུག་>སྟེ།                                                                          |
| མི་འཇུག་སའི་ཡུལ།     | illegal agreement female     | <pp...>         |                                                                                                            |
| མི་འཇུག་ས།         | illegal agreement male       | <pp*...>        |                                                                                                            |
| ས་བཅད།           | outline                      | <q........q>    |                                                                                                            |
| ས་བཅད་ཀྱི་དབྱེ་གཞི།   | outline node                 | <q*........>    |                                                                                                            |
| ས་བཅད་ཀྱི་ནང་གསེས།  | outline branches             | <q**........>   |                                                                                                            |
| ངོས་འཛིན་བྱ།        | what is identified           | <r.........>    |                                                                                                            |
| ངོས་འཛིན་བྱེད།       | identification               | <r*.........>   |                                                                                                            |
| རྩ་བ།             | root text                    | <m.........m>   | <mསྦྱིན་དང་ཚུལ་ཁྲིམས་བཟོད་དང་བརྩོན་འགྲུས་དང༌། །བསམ་གཏན་ཤེས་རབ་ཕ་རོལ་ཕྱིན་པ་དྲུགm>།ཅེས་གསུངས་པ་ལྟར།                             |
| འགྲེལ་བ།           | commentary                   | <m*.........>   |                                                                                                            |


### Source text pagination tags
`[1a]` folio, side

`[1a.1]` folio, side, line

### TOC tags
`{T###}` text ID

`{T###-##}` section/chapter ID

### Layout tags

| བོད། bo         | ཨིན། en                                                  | རྟགས། tag    | དཔེར་བརྗོད། Example                                                                                           |
| -------------- | ------------------------------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------- |
| ཡིག་ཆུང་།        | contains smaller text size                              | \<y...y\>     | \<yབཤད་སྒྲུབ་བསྟན་པའི་འབྱུང་གནས་དཔལ་ལྡན་བཀྲ་ཤིས་འཁྱིལ་དུ་རབ་བྱུང་བཅུ་བཞི་པའི་ལྕགས་སྤྲེལ་གྱི་ལོར་པར་དུ་བསྐྲུན་པ་དགེ་ལེགས་འཕེལ།  སརྦ་མངྒ་ལཾ། །y\> |
| མཛད་པ་པོ།       | Name\<s\> of an author, personal or corporate, of a work. | \<au....\>    | \<auམཛད་པ་པོ། མཁས་གྲུབ་ཀརྨ་ཆགས་མེད། གཏེར་ཆེན་ཀརྨ་གླིང་པ།\>                                                             |
| དཔེ་ཆའི་མཚན་བྱང་། | contains pecha title                                    | \<k1.......\> | \<k1བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ་བཞུགས་སོ།།\>                                                                    |
| པོ་ཏིའི་མཚན་བྱང་།  | contains poti title                                     | \<k2.......\> | \<k2༄༅། །འདུལ་བ་ཀ་བཞུགས་སོ། །\>                                                                                 |
| ལེའུ་ཡི་མཚན་བྱང་།  | contains chapter title                                  | \<k3.......\> | \<k3དཀོན་མཆོག་གསུམ་ལ་ཕྱག་འཚལ་ལོ། །\>                                                                              |

 `#\<Peydurma\>` denotes the peydurma notes. Eg #དག་འཇོག་པར་བྱེད་པས་བདག་ཅག་རེ་ཞིག་བཅོམ་ལྡན་འདས་ལ་བལྟ་བ་དང་བསྙེན་བཀུར་བྱ་བའི་ཕྱིར་འདོང་བ་སྔས་ཀྱིས།

### Spell-checking tags

`\<error,suggestion\>` potential error, correction suggestion

### Critical aparatus
`[ ]` uncertain reading

`\<* \>`  editorial restoration of lost text

`⟨* ⟩`  editorial addition of omitted text

`⟪ ⟫` scribal insertion

`{ }` editorial deletion of redundant text

`{{ }}` scribal deletion

`///` textual loss at left or right edge of support

## Notes

- we don't encode lines as annotations and generate them on the fly from the pagination layer and line returns in the base

## Sources
- [gandhari.org]\<https://gandhari.org/a_dpreface.php\>
- [esukhia/derge-kangyur]\<https://github.com/Esukhia/derge-kangyur\>



  
  
<\details>


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
