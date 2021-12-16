# Annotations

All the annotations in OPF are just span of start and end character the base layer and some attributes of the particular annotation. The most simplest form of annotation is just having the a span. Here is the list of annotation currently supported by OpenPecha.

Annotations in OpenPecha are broadly categorized into **Physical** and **Semantic** annotations.


## Semantic Annotations

Any annotations from the **Verbal text**

### Citation

Citation

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Citation_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Citation_tutorial.py!}
```
</details>

### Correction

Correction

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Citation_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Citation_tutorial.py!}
```
</details>

### ErrorCandidate
ErrorCandidate

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/ErrorCandidate_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/ErrorCandidate_tutorial.py!}
```
</details>

### Pedurma
Pedurma

<details>
<summary>JSON Schema:</summary>
```json
{!../../docs_src/annotations/Pedurma_schema.json!}
```
</details>

<details>
<summary>Python example:</summary>
```python
{!../../docs_src/annotations/Pedurma_tutorial.py!}
```
</details>


### Sabche
Sabche

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Sabche_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Sabche_tutorial.py!}
```
</details>

### Tsawa
Tsawa

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Tsawa_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Tsawa_tutorial.py!}
```
</details>

### Yigchung
Yigchung

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Yigchung_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Yigchung_tutorial.py!}
```
</details>

### Archaic
Archaic

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Archaic_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Archaic_tutorial.py!}
```
</details>

### Durchen
Durchen

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Durchen_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Durchen_tutorial.py!}
```
</details>

### Footnote
Footnote

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Footnote_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Footnote_tutorial.py!}
```
</details>

### Segment
Segment of an alignment

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Segment_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Segment_tutorial.py!}
```
</details>

## Physical Annotations

### BookTitle

Title of the book

### SubTitle

Sub title of the book

### Edition

It can be Edition number/name. Previously called *BookNumber*.

### Author

author of the book

### Chapter

Chapter title

### Text

Represents text and used in *Index* layer.

### SubText

Represents Sub text and used in *Index* layer.

### Pagination

Represents the single page of a text.

<details>
<summary>JSON Schema</summary>
```json
{!../../docs_src/annotations/Pagination_schema.json!}
```
</details>

<details>
<summary>Python example</summary>
```python
{!../../docs_src/annotations/Pagination_tutorial.py!}
```
</details>