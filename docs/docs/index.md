# Introduction

## Why OpenPecha?

Digital text is quickly becoming essential to modern daily life. The article you’re reading right now is born digital; unlike texts of the not-so-distant past, it may never be printed at all. Worldwide, the trend is clear: Digital text is on the way in, and print is on its way out. Year-by-year, more and more readers are turning to ebooks, internet news, and other forms of ereading, while generation-by-generation, print is becoming less and less relevant.

These trends aren’t unique to English—to meet the demands and expectations of today’s readers, Tibetan texts, too, are being digitized by many organizations and institutions with a shared appreciation for the Tibetan literary heritage. They include a variety of secular publishers, monastic institutions, and Buddhist foundations, among others. But while these organizations share common goals for common texts, their work is all too frequently completely disconnected from the community at large.

This situation negatively impacts what is already a minoritized and under-resourced language. While competition—from other languages, as well as other publishers in the Tibetan etext world—has been a driver of innovation in the adoption of ereading technology, we believe that a rich, shared data source is not only in everyone’s best interest, but the only practical way forward when we consider the time, effort, expertise, and money that quality digitization takes.

That’s why we’ve designed OpenPecha to be a public, open platform for collaborative etext curation and annotation sharing. Its aim is providing a wide range of users with the latest version of the exact “view” of any text they need, while maintaining the integrity of the text and its annotations, and simultaneously allowing for community improvements and additions. In this paper, we explore the details of how the project came to be; what it is and how it works; while also presenting a few common use cases.

## What is OpenPecha?

As we’ve touched on above, a truly modern digital publication is never a “final”, static image. Instead, it’s a living, breathing entity in constant communication with its community. The Tibetan digital landscape needs an open space where data can be gathered; on offer to anyone in the community; and open to collaborative curation and annotation, while also responding to users’ needs. This kind of public-domain, digital publishing will be familiar to anyone who’s heard of Project Gutenburg and its Distributed Proofreaders platform, and the offshoots they’ve inspired (GITenberg, WikiBooks, etc.). From a practical standpoint, that means we need a tool that imports from, and exports to, formats common to users who access Tibetan texts; that transfers annotations from one base text to another; and that offers an organized, systematic catalog of titles, versions, annotations, and related texts. This data-first maintenance and interoperability are the core aims of OpenPecha’s database, format, and toolkit.

First, it aims to store every available electronic representation of each text, along with all existing annotations. From there, both the texts and their annotations are downloadable; contributions are uploadable; and users can export to a variety of common formats (like EPUB and PDF). This means that texts can keep improving while not losing any of their annotations. It also allows for any NLP (Natural Language Processing), NER (Named Entity Recognition), or error-detecting models to be applied to the entirety of the corpus without interfering with existing data created by others. Finally, it gives the community of readers access to the most-current proofread ebooks that contain only the annotation layers they need, in the format of their choice. In short, the goal is to provide something that is:

- **Flexible** in application, serving a wide variety of Tibetan language professionals;
- **Durable** in that it uses free tools and platforms, with minimal maintenance;
- **Editable** at all stages of the workflow, and at every level of the document;
- **Easy-to-learn** and human-friendly for the average user;
- **Open** to anyone anywhere, providing a large catalog of texts with a wide range of annotation schema; and
- **Collaborative**, to leverage shared knowledge in a small, specialized field, and allow for crowdsourced improvements.

## Who is OpenPecha for?
- **Text Owners**. Text owners are groups of people who are linked to a particular Tibetan text through their history, culture, and heritage, and have a continuing relationship that brings the text into living, communicative contexts; this includes, for example, living monastic traditions that study the particular texts of their Buddhist lineage or research projects who specialize in a given collection
    - Find contributors for their own collections
    - Manage pechas in their own collections (admin Master branches)

- **Academics & Researchers** in Tibetan Studies; Philology; Digital Humanities; Linguistics; Monastic Settings; or any other field who need to access, read, translate, edit, or annotate Tibetan texts. OPF allows them to:
    - Build custom corpuses with any annotations they like
    - Contribute texts or annotations
    - Update texts and annotations
    - Export works in their preferred format

- **Publishers**
    - Download the best & latest version of a text
    - Download or contribute annotations
    - Export in preferred format (EPUB for publishing, etc.)

- **Digital Libraries**
    - Connect their user interface to OpenPecha to fetch etexts and the annotations they need (IIIF, International Image Interoperability Framework, for image libraries, etc.)
    - Update and contribute new annotations via Github API
    - Add improvements to the toolkit according to their needs
    - Use OpenPecha as an editing tool for updating their content as part of a dynamic publishing workflow

- **Readers**
    - Export the latest & best version of a text in their preferred format

- **Programmers**
    - Link to the best version of texts with annotations through API (Application Programming Interface)
