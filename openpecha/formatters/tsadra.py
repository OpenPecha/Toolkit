import os
from copy import deepcopy
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup

from .formatter import BaseFormatter
from .layers import *
from .layers import AnnType


class TsadraTemplate:
    """Content tsadra template components.
    """

    author = [
        "credits-page_front-page---text-author",
        "credits-page_front-page---text-author1",
    ]
    titles = [
        "credits-page_front-title",
        "tibetan-book-title",
        "tibetan-book-sub-title",
    ]
    chapters = ["", "", ""]
    commentaries = {
        "verse": [
            "tibetan-commentary-first-line",
            "tibetan-commentary-middle-lines",
            "tibetan-commentary-last-line",
        ],
        "non-verse": [
            "tibetan-commentary-non-indent1",
            "tibetan-commentary-non-indent",
            "tibetan-regular-indented",
        ],
    }
    citation_base = "tibetan-citations-in-verse_tibetan-citations"
    citation_first_line = f"{citation_base}-first-line"
    citation_middle_lines = f"{citation_base}-middle-lines"
    citation_last_line = f"{citation_base}-last-line"
    citation_indent = "tibetan-citations-in-verse_tibetan-regular-indented"
    citation_inline = "tibetan-external-citations"
    tsawa_base = "tibetan-root-text_tibetan-root-text"
    tsawa_first_line = f"{tsawa_base}-first-line"
    tsawa_middle_lines = f"{tsawa_base}-middle-lines"
    tsawa_last_line = f"{tsawa_base}-last-line"
    tsawa_oneliner = [f"{tsawa_base}-1-line-only", ""]
    tsawa_inline = "tibetan-root-text"
    sabches = ["tibetan-sabche", "tibetan-sabche1"]
    yigchung = "tibetan-commentary-small"


class TsadraFormatter(BaseFormatter):
    """
    OpenPecha Formatter for Tsadra DarmaCloud ebooks
    """

    def __init__(self, output_path="./output"):
        super().__init__(output_path=output_path)
        self.base_text = ""
        self.cover_image = ""
        self.walker = 0  # The walker to traverse every character in the pecha
        self.book_title = []  # list variable to store book title index
        self.poti_title = []
        self.author = []  # list variable to store author annotion index
        self.chapter = []  # list variable to store chapter annotation index
        self.topic = []
        self.sub_topic = []
        self.pagination = []
        self.root_text = []  # list variable to store root text index
        self.citation = []  # list variable to store citation index
        self.sabche = []  # list variable to store sabche index
        self.yigchung = []  # list variable to store yigchung index

    def text_preprocess(self, text):
        return text

    def get_cover_image(self, soup):
        divs = soup.find_all("div", {"epub:type": "cover"})
        if divs:
            return divs[0].img["src"].split("/")[1]
        return ""

    def parse_ann(self, ann, tmp_text, walker, isverse=None):
        if isverse is not None:
            return (
                None,
                ann(Span(walker, len(tmp_text) - 1 + walker), isverse=isverse),
            )
        else:
            return (None, ann(Span(walker, len(tmp_text) - 1 + walker)))

    def build_layers(self, html):
        """
        To Build the layer
        """
        soup = BeautifulSoup(html, "html.parser")
        book_title_tmp = ""
        author_tmp = ""
        chapter_title_tmp = ""
        root_text_tmp = ""
        sabche_tmp = ""
        commentary_tmp = ""
        citation_tmp = ""
        cover = self.get_cover_image(soup)
        if cover:
            self.cover_image = cover
        ps = soup.find_all("p")
        for p in ps:
            if p["class"][0] in TsadraTemplate.titles:  # to get the book title index
                book_title_tmp = self.text_preprocess(p.text)
                self.book_title.append(
                    self.parse_ann(BookTitle, book_title_tmp, self.walker)
                )
                self.base_text += book_title_tmp + "\n"
                self.walker += len(book_title_tmp) + 1

            elif (
                p["class"][0] in TsadraTemplate.author
            ):  # to get the author annotation index
                author_tmp = self.text_preprocess(p.text)
                self.author.append(self.parse_ann(Author, author_tmp, self.walker))
                self.base_text += author_tmp + "\n"
                self.walker += len(author_tmp) + 1

            elif (
                TsadraTemplate.tsawa_base in p["class"][0]
            ):  # to get the root text or 'tsawa' annotation index (verse form)
                # TODO: one line root text.
                if (
                    p["class"][0] == TsadraTemplate.tsawa_first_line
                    or p["class"][0] == TsadraTemplate.tsawa_middle_lines
                ):
                    root_text_tmp += self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(p.text) + "\n"
                elif p["class"][0] == TsadraTemplate.tsawa_last_line:
                    for s in p.find_all("span"):
                        if "root" in s["class"][0]:
                            root_text_tmp += self.text_preprocess(s.text)
                            self.root_text.append(
                                self.parse_ann(
                                    Tsawa, root_text_tmp, self.walker, isverse=True
                                )
                            )
                            self.walker += len(root_text_tmp) + 1
                            root_text_tmp = ""
                        else:
                            self.walker += len(self.text_preprocess(s.text))
                    self.base_text += self.text_preprocess(p.text) + "\n"
                else:
                    for s in p.find_all("span"):
                        if "root" in s["class"][0]:
                            root_text_tmp += self.text_preprocess(s.text)
                            self.root_text.append(
                                self.parse_ann(
                                    Tsawa, root_text_tmp, self.walker, isverse=True
                                )
                            )
                            self.walker += len(root_text_tmp) + 1
                            root_text_tmp = ""
                        else:
                            self.walker += len(self.text_preprocess(s.text))
                    self.base_text += self.text_preprocess(p.text) + "\n"

            elif "tibetan-chapter" in p["class"][0]:  # to get chapter title index
                chapter_title_tmp = self.text_preprocess(p.text)
                self.chapter.append(
                    self.parse_ann(Chapter, chapter_title_tmp, self.walker)
                )
                self.walker += len(chapter_title_tmp) + 1
                self.base_text += chapter_title_tmp + "\n"

            elif (
                p["class"][0] in TsadraTemplate.commentaries["verse"]
                or p["class"][0] in TsadraTemplate.commentaries["non-verse"]
            ):

                # travesing through commetary which are in verse form
                if p["class"][0] == TsadraTemplate.commentaries["verse"]:
                    commentary_tmp += self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(p.text) + "\n"
                    self.walker += len(commentary_tmp)
                    commentary_tmp = ""
                # travesing through each span of commentary and regular ptag to search annotations
                else:
                    p_tmp = ""
                    p_walker = self.walker
                    for s in p.find_all("span"):
                        try:
                            s["class"][0]
                        except Exception:
                            p_tmp += self.text_preprocess(s.text)
                            continue

                        if (
                            s["class"][0] == TsadraTemplate.yigchung
                        ):  # checking for yigchung annotation
                            if citation_tmp:
                                # citation_tmp += citation_tmp
                                self.citation.append(
                                    self.parse_ann(
                                        Citation, citation_tmp, p_walker, isverse=False
                                    )
                                )
                                p_walker += len(citation_tmp)
                                citation_tmp = ""

                            if sabche_tmp:
                                self.sabche.append(
                                    self.parse_ann(Sabche, sabche_tmp, p_walker)
                                )
                                p_walker += len(sabche_tmp)
                                sabche_tmp = ""

                            self.yigchung.append(
                                self.parse_ann(Yigchung, s.text, p_walker)
                            )
                            p_walker += len(self.text_preprocess(s.text))

                        elif (
                            s["class"][0] == TsadraTemplate.citation_inline
                        ):  # checking for citation annotation
                            citation_tmp += self.text_preprocess(s.text)

                        elif (
                            "sabche" in s["class"][0]
                        ):  # checking for citation annotation
                            sabche_tmp += self.text_preprocess(s.text)

                        elif "front-title" in s["class"][0]:
                            if citation_tmp:
                                self.citation.append(
                                    self.parse_ann(
                                        Citation, citation_tmp, p_walker, isverse=False
                                    )
                                )
                                p_walker += len(citation_tmp)
                                citation_tmp = ""
                            if sabche_tmp:
                                self.sabche.append(
                                    self.parse_ann(Sabche, sabche_tmp, p_walker)
                                )
                                p_walker += len(sabche_tmp)
                                sabche_tmp = ""
                            p_walker += len(self.text_preprocess(s.text))
                        else:
                            if citation_tmp:
                                self.citation.append(
                                    self.parse_ann(
                                        Citation, citation_tmp, p_walker, isverse=False
                                    )
                                )
                                p_walker += len(citation_tmp)
                                citation_tmp = ""

                            if sabche_tmp:
                                self.sabche.append(
                                    self.parse_ann(Sabche, sabche_tmp, p_walker)
                                )
                                p_walker += len(sabche_tmp)
                                sabche_tmp = ""

                            p_walker += len(self.text_preprocess(s.text))

                    # when citation ends the para
                    if citation_tmp:
                        self.citation.append(
                            self.parse_ann(
                                Citation, citation_tmp, p_walker, isverse=False
                            )
                        )
                        p_walker += len(citation_tmp)
                        citation_tmp = ""

                    if sabche_tmp:
                        self.sabche.append(self.parse_ann(Sabche, sabche_tmp, p_walker))
                        p_walker += len(sabche_tmp)
                        sabche_tmp = ""

                    commentary_tmp = self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(commentary_tmp)
                    self.walker += len(commentary_tmp)
                    commentary_tmp = ""
                    p_walker = 0

            elif (
                p["class"][0] in TsadraTemplate.sabches
            ):  # checking for sabche annotation
                sabche_tmp = ""
                p_with_sabche_tmp = ""
                sabche_walker = self.walker
                for s in p.find_all("span"):
                    try:
                        s["class"][0]
                    except Exception:
                        p_with_sabche_tmp += self.text_preprocess(s.text)
                        continue

                    if "sabche" in s["class"][0]:
                        sabche_tmp += self.text_preprocess(s.text)

                    else:
                        if sabche_tmp:
                            self.sabche.append(
                                self.parse_ann(Sabche, sabche_tmp, sabche_walker)
                            )
                            sabche_walker = len(sabche_tmp) + sabche_walker
                            sabche_tmp = ""
                        sabche_walker += len(self.text_preprocess(s.text))

                # when sabche ends the para
                if sabche_tmp:
                    self.sabche.append(
                        self.parse_ann(Sabche, sabche_tmp, sabche_walker)
                    )
                    sabche_tmp = ""
                self.walker += len(self.text_preprocess(p.text)) + 1
                self.base_text += self.text_preprocess(p.text) + "\n"
                sabche_walker = 0
            elif (
                TsadraTemplate.citation_base in p["class"][0]
            ):  # checking for citation annotation first two if for verse form and last for non verse
                if (
                    p["class"][0] == TsadraTemplate.citation_first_line
                    or p["class"][0] == TsadraTemplate.citation_middle_lines
                ):
                    citation_tmp += self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(p.text) + "\n"
                elif p["class"][0] == TsadraTemplate.citation_last_line:
                    citation_tmp += self.text_preprocess(p.text) + "\n"
                    self.citation.append(
                        self.parse_ann(
                            Citation, citation_tmp, self.walker, isverse=True
                        )
                    )
                    self.base_text += self.text_preprocess(p.text) + "\n"
                    self.walker += len(citation_tmp)
                    citation_tmp = ""
                elif p["class"][0] == TsadraTemplate.citation_indent:
                    citation_tmp += self.text_preprocess(p.text)
                    self.base_text += self.text_preprocess(p.text) + "\n"
                    self.citation.append(
                        self.parse_ann(
                            Citation, citation_tmp, self.walker, isverse=True
                        )
                    )
                    self.walker += len(citation_tmp) + 1
                    citation_tmp = ""
            else:
                if p.text:
                    self.base_text += self.text_preprocess(p.text) + "\n"
                    self.walker += len(self.text_preprocess(p.text)) + 1

    def get_result(self):
        """
        To return all the result
        """
        result = {
            AnnType.book_title: [self.book_title],
            AnnType.poti_title: [self.poti_title],
            AnnType.author: [self.author],
            AnnType.chapter: [self.chapter],
            AnnType.topic: [self.topic],
            AnnType.sub_topic: [self.sub_topic],
            AnnType.pagination: [self.pagination],
            AnnType.tsawa: [self.root_text],
            AnnType.citation: [self.citation],
            AnnType.sabche: [self.sabche],
            AnnType.yigchung: [self.yigchung],
        }
        return result

    def _get_meta_data(ann):
        return ",".join([self.base_text[a[0] : a[1] + 1] for a in ann])

    def get_base_text(self):
        """
        To return base text of each processed page
        """
        return self.base_text

    def get_input(self, input_path):
        def get_prefix(html_paths):
            self.sku = list(html_paths[0].parents)[1].name
            return sorted(html_paths, key=lambda p: len(p.stem))[0].stem

        def semantic_order(sku, html_path):
            html_fn = html_path.stem
            order = html_fn[len(sku) + 1 :]
            if order:
                return int(order)
            else:
                return 0

        html_paths = [
            o
            for o in input_path.iterdir()
            if o.suffix == ".xhtml" and o.stem != "cover"
        ]
        sku_sementic_order = partial(semantic_order, get_prefix(html_paths))
        html_paths = sorted(html_paths, key=sku_sementic_order)
        html_paths.insert(0, input_path / "cover.xhtml")

        for html_fn in html_paths:
            yield Path(html_fn).read_text()

    def create_metadata(self, layers):
        def get_text(span):
            return self.base_text[span["start"] : span["end"] + 1].replace("\n", "")

        meta_data = {}
        meta_data["title"] = get_text(layers["BookTitle"][0][1][0][1]["span"])
        meta_data["authors"] = [
            get_text(span["span"]) for (layer, span) in layers["Author"][0][1]
        ]
        meta_data["sku"] = self.sku
        meta_data["cover"] = self.cover_image
        meta_data["layers"] = [layer for layer in layers if layers[layer]]
        return {"ebook_metadata": meta_data}

    def create_opf(self, input_path, id_):
        input_path = Path(input_path)
        self._build_dirs(input_path, id_=id_)
        (self.dirs["opf_path"] / "base").mkdir(exist_ok=True)

        # cover image path
        image_path = input_path / "image"
        (self.dirs["opf_path"] / "asset").mkdir(exist_ok=True)
        os.system(f"cp -R {image_path} {self.dirs['opf_path']}/asset")

        # parse layers
        for html in self.get_input(input_path):
            self.build_layers(html)

        # save base-text
        (self.dirs["opf_path"] / "base" / "v001.txt").write_text(self.get_base_text())

        # format and save layer
        vol_layer_path = self.dirs["layers_path"] / "v001"
        vol_layer_path.mkdir(exist_ok=True)
        layers = self.get_result()
        for vol_layer, base_id in self.format_layer(layers):
            for layer, ann in vol_layer.items():
                if ann["annotations"]:
                    if layer == "index":
                        layer_fn = self.dirs["opf_path"] / f"{layer}.yml"
                    else:
                        layer_fn = vol_layer_path / f"{layer}.yml"
                    self.dump(ann, layer_fn)

        # save metatdata
        meta_data = self.create_metadata(layers)
        meta_fn = self.dirs["opf_path"] / "meta.yml"
        self.dump(meta_data, meta_fn)


# if __name__ == "__main__":
#     path = "./P000100/OEBPS/"
#     formatter = TsadraFormatter(output_path="./test_opf")
#     formatter.create_opf(path, 1)
