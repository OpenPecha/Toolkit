from copy import deepcopy
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup

from .formatter import BaseFormatter
from .layers import *
from .layers import AnnType


class TsadraFormatter(BaseFormatter):
    """
    OpenPecha Formatter for Tsadra DarmaCloud ebooks
    """

    def __init__(self, output_path="./opfs"):
        super().__init__(output_path=output_path)
        self.base_text = ""
        self.walker = 0  # The walker to traverse every character in the pecha
        self.book_title = []  # list variable to store book title index
        self.author = []  # list variable to store author annotion index
        self.chapter = []  # list variable to store chapter annotation index
        self.root_text = []  # list variable to store root text index
        self.citation = []  # list variable to store citation index
        self.sabche = []  # list variable to store sabche index
        self.yigchung = []  # list variable to store yigchung index

    def text_preprocess(self, text):
        return text

    def add_new_ann(self, layer, ann):
        uuid = self.get_unique_id()
        layer["annotations"][uuid] = ann

    def create_new_layer(self, layer_name, anns):
        new_layer = Layer(self.get_unique_id(), layer_name)
        for ann in anns:
            self.add_new_ann(new_layer, ann)
        return new_layer

    def format_layer(self, layers):

        cross_vol_anns, non_cross_vol_anns = [], []
        for layer_name, layer_anns in layers.items():
            if layer_name in ["topic", "sub_topic"]:
                cross_vol_anns.append((layer_name, layer_anns))
            else:
                non_cross_vol_anns.append((layer_name, layer_anns))

        del layers

        # Create Annotaion layers
        for (i, vol_layers) in enumerate(non_cross_vol_anns):
            base_id = f"v{i+1:03}"

            result = {}
            layer_name, layer_anns = vol_layers
            result[layer_name] = self.create_new_layer(layer_name, layer_anns)
            yield result, base_id

        # Create Index layer
        Index_layer = Layer(self.get_unique_id(), "index")
        # loop over each topic
        for topic, sub_topic in zip(*cross_vol_anns):
            Topic = deepcopy(Text)
            Topic["id"] = self.get_unique_id()

            # loop over each sub_topic
            for cross_sub_topic in sub_topic:
                sub_text = deepcopy(SubText)
                sub_text["id"] = self.get_unique_id()
                for start, end, vol_id, work in cross_sub_topic:
                    sub_text["work"] = work
                    cross_vol_span = deepcopy(CrossVolSpan)
                    cross_vol_span["vol"] = f"base/v{vol_id:03}"
                    cross_vol_span["span"]["start"] = start
                    cross_vol_span["span"]["end"] = end
                    sub_text["span"].append(cross_vol_span)

                if corss_sub_topic:
                    Topic["parts"].append(sub_text)

            for start, end, vol_id, work in topic:
                Topic["work"] = work
                cross_vol_span = deepcopy(CrossVolSpan)
                cross_vol_span["vol"] = f"base/v{vol_id:03}"
                cross_vol_span["span"]["start"] = start
                cross_vol_span["span"]["end"] = end
                Topic["span"].append(cross_vol_span)

            Index_layer["annotations"].append(Topic)

        result = {"index": Index_layer}

        yield result, None

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
        rt_base = "tibetan-root-text_tibetan-root-text"
        cit_base = "tibetan-citations-in-verse_"
        com_base = "tibetan-commentary"
        com_classes = {
            "first": f"{com_base}-first-line",
            "middle": f"{com_base}-middle-lines",
            "last": f"{com_base}-last-line",
            "non": f"{com_base}-non-indent1",
        }
        cit_classes = {
            "first": f"{cit_base}tibetan-citations-first-line",
            "middle": f"{cit_base}tibetan-citations-middle-lines",
            "last": f"{cit_base}tibetan-citations-last-line",
            "indent": f"{cit_base}tibetan-regular-indented",
        }
        root_text_classes = {
            "first": f"{rt_base}-first-line",
            "middle": f"{rt_base}-middle-lines",
            "last": f"{rt_base}-last-line",
        }
        # p_with_citations = []
        ps = soup.find_all("p")
        for p in ps:
            if "credits-page_front-title" in p["class"][0]:  # to get the book title index
                book_title_tmp = self.text_preprocess(p.text) + "\n"
                self.book_title.append(
                    {"span": {"start": self.walker, "end": len(book_title_tmp) - 1 + self.walker}}
                )
                self.base_text += book_title_tmp
                self.walker += len(book_title_tmp)

            if "text-author" in p["class"][0]:  # to get the author annotation index
                author_tmp = self.text_preprocess(p.text) + "\n"
                self.author.append(
                    {"span": {"start": self.walker, "end": len(author_tmp) - 1 + self.walker}}
                )
                self.base_text += author_tmp
                self.walker += len(author_tmp)

            if (
                rt_base in p["class"][0]
            ):  # to get the root text or 'tsawa' annotation index (verse form)
                # TODO: one line root text.
                if (
                    p["class"][0] == root_text_classes["first"]
                    or p["class"][0] == root_text_classes["middle"]
                ):
                    root_text_tmp += self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(p.text) + "\n"
                elif p["class"][0] == root_text_classes["last"]:
                    for s in p.contents:
                        if "root" in s["class"][0]:
                            root_text_tmp += self.text_preprocess(s.text)
                            self.root_text.append(
                                {
                                    "span": {
                                        "start": self.walker,
                                        "end": len(root_text_tmp) - 1 + self.walker,
                                    },
                                    "isverse": True,
                                }
                            )
                            self.walker += len(root_text_tmp) + 1
                            root_text_tmp = ""
                        else:
                            self.walker += len(self.text_preprocess(s.text))
                    self.base_text += self.text_preprocess(p.text) + "\n"

            elif "tibetan-chapter" in p["class"][0]:  # to get chapter title index
                chapter_title_tmp = self.text_preprocess(p.text) + "\n"
                self.chapter.append(
                    {
                        "span": {
                            "start": self.walker,
                            "end": len(chapter_title_tmp) - 1 + self.walker,
                        }
                    }
                )
                self.walker += len(chapter_title_tmp)
                self.base_text += chapter_title_tmp

            elif "commentary" in p["class"][0] or "tibetan-regular-indented" in p["class"][0]:

                # travesing through commetary which are in verse form
                if p["class"][0] == com_classes["first"] or p["class"][0] == com_classes["middle"]:
                    commentary_tmp += self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(p.text) + "\n"
                elif p["class"][0] == com_classes["last"]:
                    commentary_tmp += self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(p.text) + "\n"
                    self.walker += len(commentary_tmp)
                    commentary_tmp = ""
                # travesing through each span of commentary and regular ptag to search annotations
                else:
                    p_tmp = ""
                    p_walker = self.walker
                    for s in p.contents:
                        # check for page with no content and skip the page
                        if isinstance(s, str):
                            return ""
                        # some child are not <span> rather like <a> and some <span> has no 'class' attr
                        try:
                            s["class"][0]
                        except:
                            p_tmp += self.text_preprocess(s.text)
                            continue

                        if "small" in s["class"][0]:  # checking for yigchung annotation
                            # p_tmp += f'{{++*++}}{self.text_preprocess(s.text)}{{++*++}}'
                            if citation_tmp:
                                # citation_tmp += citation_tmp
                                self.citation.append(
                                    {
                                        "span": {
                                            "start": p_walker,
                                            "end": len(citation_tmp) + p_walker - 1,
                                        },
                                        "isverse": False,
                                    }
                                )
                                p_walker += len(citation_tmp)
                                citation_tmp = ""
                            self.yigchung.append(
                                {
                                    "span": {
                                        "start": p_walker,
                                        "end": len(self.text_preprocess(s.text)) - 1 + p_walker,
                                    }
                                }
                            )
                            p_walker += len(self.text_preprocess(s.text))

                        elif (
                            "external-citations" in s["class"][0]
                        ):  # checking for citation annotation
                            citation_tmp += self.text_preprocess(s.text)

                        elif "front-title" in s["class"][0]:
                            if citation_tmp:
                                self.citation.append(
                                    {
                                        "span": {
                                            "start": p_walker,
                                            "end": len(citation_tmp) + p_walker - 1,
                                        },
                                        "isverse": False,
                                    }
                                )
                                p_walker += len(citation_tmp)
                                citation_tmp = ""
                            p_walker += len(self.text_preprocess(s.text))
                        else:
                            if citation_tmp:
                                self.citation.append(
                                    {
                                        "span": {
                                            "start": p_walker,
                                            "end": len(citation_tmp) + p_walker - 1,
                                        },
                                        "isverse": False,
                                    }
                                )
                                p_walker += len(citation_tmp)
                                citation_tmp = ""
                            p_walker += len(self.text_preprocess(s.text))

                    # when citation ends the para
                    if citation_tmp:
                        self.citation.append(
                            {
                                "span": {
                                    "start": p_walker,
                                    "end": len(citation_tmp) + p_walker - 1,
                                },
                                "isverse": False,
                            }
                        )
                        p_walker += len(citation_tmp)
                        citation_tmp = ""

                    commentary_tmp = self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(commentary_tmp)
                    self.walker += len(commentary_tmp)
                    commentary_tmp = ""
                    p_walker = 0

            elif "sabche" in p["class"][0]:  # checking for sabche annotation
                sabche_tmp = ""
                p_with_sabche_tmp = ""
                sabche_walker = self.walker
                for s in p.contents:
                    try:
                        s["class"][0]
                    except:
                        p_with_sabche_tmp += self.text_preprocess(s.text)
                        continue

                    if "sabche" in s["class"][0]:
                        sabche_tmp += self.text_preprocess(s.text)

                    elif "front-tile" in s["class"][0]:
                        sabche_walker += len(self.text_preprocess(s.text))

                # when sabche ends the para
                if sabche_tmp:
                    self.sabche.append(
                        {"span": {"start": sabche_walker, "end": len(sabche_tmp) + sabche_walker,}}
                    )
                    sabche_tmp = ""
                self.walker += len(self.text_preprocess(p.text)) + 1
                self.base_text += self.text_preprocess(p.text) + "\n"
                sabche_walker = 0
            elif (
                cit_base in p["class"][0]
            ):  # checking for citation annotation first two if for verse form and last for non verse
                if p["class"][0] == cit_classes["first"] or p["class"][0] == cit_classes["middle"]:
                    citation_tmp += self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(p.text) + "\n"
                elif p["class"][0] == cit_classes["last"]:
                    citation_tmp += self.text_preprocess(p.text) + "\n"
                    self.citation.append(
                        {
                            "span": {
                                "start": self.walker,
                                "end": len(citation_tmp) - 1 + self.walker,
                            },
                            "isverse": True,
                        }
                    )
                    self.base_text += self.text_preprocess(p.text) + "\n"
                    self.walker += len(citation_tmp)
                    citation_tmp = ""
                elif p["class"][0] == cit_classes["indent"]:
                    citation_tmp += self.text_preprocess(p.text) + "\n"
                    self.base_text += self.text_preprocess(p.text) + "\n"
                    self.citation.append(
                        {
                            "span": {
                                "start": self.walker,
                                "end": len(citation_tmp) - 1 + self.walker,
                            },
                            "isverse": True,
                        }
                    )
                    self.walker += len(citation_tmp)
                    citation_tmp = ""

    def get_result(self):
        """
        To return all the result
        """
        result = {
            AnnType.book_title: self.book_title,
            AnnType.author: self.author,
            AnnType.chapter: self.chapter,
            AnnType.tsawa: self.root_text,
            AnnType.citation: self.citation,
            AnnType.sabche: self.sabche,
            AnnType.yigchung: self.yigchung,
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
            o for o in input_path.iterdir() if o.suffix == ".xhtml" and o.stem != "cover"
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
        meta_data["title"] = get_text(layers["Book Title"][0]["span"])
        meta_data["authors"] = [get_text(span["span"]) for span in layers["Author"]]
        meta_data["sku"] = self.sku
        meta_data["layers"] = [l for l in layers if layers[l]]
        return {"ebook_metadata": meta_data}

    def create_opf(self, input_path, id):
        input_path = Path(input_path)
        self._build_dirs(input_path, id=id)
        (self.dirs["opf_path"] / "base").mkdir(exist_ok=True)

        # parse layers
        for html in self.get_input(input_path):
            self.build_layers(html)

        # save base-text
        (self.dirs["opf_path"] / "base" / f"v001.txt").write_text(self.get_base_text())

        # format and save layer
        vol_layer_path = self.dirs["layers_path"] / "v001"
        vol_layer_path.mkdir(exist_ok=True)
        layers = self.get_result()
        for vol_layer, base_id in self.format_layer(layers):
            for layer, ann in vol_layer.items():
                if ann["annotations"]:
                    layer_fn = vol_layer_path / f"{layer}.yml"
                    self.dump(ann, layer_fn)

        # save metatdata
        meta_data = self.create_metadata(layers)
        meta_fn = self.dirs["opf_path"] / "meta.yml"
        self.dump(meta_data, meta_fn)


if __name__ == "__main__":
    path = "./P000100/OEBPS/"
    formatter = TsadraFormatter(output_path="./test_opf")
    formatter.create_opf(path, 1)
