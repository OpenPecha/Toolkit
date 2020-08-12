import gzip
import json
import math
import re
from pathlib import Path

import yaml

from ..utils import gzip_str
from .formatter import BaseFormatter
from .layers import *


class GoogleOCRFormatter(BaseFormatter):
    """
    OpenPecha Formatter for Google OCR JSON output of scanned pecha.
    """

    def __init__(self, output_path="./output"):
        super().__init__(output_path=output_path)
        self.n_page_breaker_char = 3
        self.page_break = "\n" * self.n_page_breaker_char
        self.base_text = []

    def text_preprocess(self, text):

        return text

    def get_input(self, input_path):
        """
        load and return all jsons in the input_path.
        """
        for fn in sorted(list(input_path.iterdir())):
            if fn.name.split(".")[0] == "info":
                continue
            try:
                yield json.load(gzip.open(str(fn), "rb")), fn.name.split(".")[0]
            except GeneratorExit:
                return None, None
            except Exception:
                yield None, None

    def _get_page_index(self, n):
        page_sides = "ab"
        div = n / 2
        page_num = math.ceil(div)
        if div.is_integer():
            return f"{page_num}{page_sides[1]}"
        else:
            return f"{page_num}{page_sides[0]}"

    def format_layer(self, layers, base_id):
        # Format page annotation
        Pagination = Layer(self.get_unique_id(), "pagination")
        for pg, page_ref in zip(layers["pages"], layers["pages_ref"]):
            uuid = self.get_unique_id()
            span = Span(pg[0], pg[1])
            page = Page(span, page_index=self._get_page_index(pg[2]), page_ref=page_ref)
            Pagination["annotations"][uuid] = page

        result = {"pagination": Pagination}

        return result

    def _get_coord(self, vertices):
        coord = []
        for vertice in vertices:
            coord.append((vertice["x"], vertice["y"]))

        return coord

    def _get_page(self, response):
        try:
            page = response["textAnnotations"][0]
        except KeyError:
            return None, None

        text = page["description"]
        # vertices = page['boundingPoly']['vertices']  # get text box

        return text, None  # self._get_coord(vertices)

    def _get_lines(self, text, last_pg_end_idx, first_pg):
        lines = []
        line_breaks = [m.start() for m in re.finditer("\n", text)]

        start = last_pg_end_idx

        # increase the start idx with page_breaker_char for page greater than frist page.
        if not first_pg:
            start += self.n_page_breaker_char + 1
            line_breaks = list(map(lambda x: x + start, line_breaks))

        for line in line_breaks:
            lines.append((start, line - 1))  # skip new_line, which has 1 char length
            start += (line - start) + 1

        return lines, line

    def save_boundingPoly(self, response, path):
        def tlbr(vertices):
            return {"tl": vertices[0], "br": vertices[2]}

        boundingPolies = {}
        for ann in response["textAnnotations"]:
            boundingPolies[ann["description"]] = tlbr(ann["boundingPoly"]["vertices"])

        zipped_boundingPolies = gzip_str(json.dumps(boundingPolies))
        path.write_bytes(zipped_boundingPolies)

    def save_low_conf_char(self, response, path):
        char_idx = 0
        low_conf_chars = ""
        for page in response["fullTextAnnotation"]["pages"]:
            for block in page["blocks"]:
                for paragraph in block["paragraphs"]:
                    for word in paragraph["words"]:
                        for symbol in word["symbols"]:
                            if symbol.get("confidence", 1) < 0.9:
                                low_conf_chars += f'{symbol["text"]} {char_idx}\n'
                            char_idx += 1
        if low_conf_chars:
            path.write_bytes(gzip_str(low_conf_chars))

    def build_layers(self, responses, vol_name, base_id=None):
        if base_id:
            bounding_poly_vol_path = (
                self.dirs["release_path"] / "bounding_poly" / base_id
            )
            low_conf_char_vol_path = (
                self.dirs["release_path"] / "low_confidence_chars" / base_id
            )
            bounding_poly_vol_path.mkdir(parents=True, exist_ok=True)
            low_conf_char_vol_path.mkdir(parents=True, exist_ok=True)

        pages = []
        pages_ref = []
        last_pg_end_idx = 0
        for response, page_ref in responses:
            # extract page number, eg: I1PD901350083 -> 83
            n_pg_str = page_ref[len(vol_name) :]
            if "-" in page_ref:
                n_pg_str = page_ref.split("-")[-1]

            if n_pg_str and n_pg_str[-1].isalpha():
                n_pg_str = n_pg_str[:-1]

            try:
                n_pg = int(n_pg_str)
            except Exception:
                # TODO: fix later, collection all the cases as of now
                n_pg = 0  # dummy value

            # extract annotation
            if not response:
                print(f"[ERROR] Failed : {n_pg}")
                continue
            text, _ = self._get_page(response)

            # skip empty page (can be bad image)
            if not text:
                print(f"[ERROR] empty page {n_pg}")
                continue
            lines, last_pg_end_idx = self._get_lines(text, last_pg_end_idx, n_pg == 1)
            pages.append((lines[0][0], lines[-1][1], n_pg))
            pages_ref.append(response.get("image_link", page_ref))

            # create base_text
            self.base_text.append(text)

            if base_id:
                # save the boundingPoly to resources
                self.save_boundingPoly(
                    response, bounding_poly_vol_path / f"{n_pg:04}.json.gz"
                )
                # save low confident char and it's corresponding index
                self.save_low_conf_char(
                    response, low_conf_char_vol_path / f"{n_pg:04}.txt.gz"
                )

        result = {"pages": pages, "pages_ref": pages_ref}

        return result

    def get_base_text(self):
        base_text = f"{self.page_break}".join(self.base_text)
        self.base_text = []

        return base_text

    def get_metadata(self, work_id):
        import xml.etree.ElementTree as ET

        import requests
        from pyewts import pyewts

        converter = pyewts()
        query_url = "https://www.tbrc.org/xmldoc?rid={}"
        bdrc_metadata_url = query_url.format(work_id)
        r = requests.get(bdrc_metadata_url)

        try:
            root = ET.fromstring(r.content.decode("utf-8"))
        except Exception:
            metadata = {
                "id": f"opecha:{self.pecha_id}",
                "initial_creation_type": "ocr",
                "source_metadata": {
                    "id": f"{work_id}",
                    "title": "",
                    "volume": "",
                    "author": "",
                },
            }
            return metadata

        title_tag = root[0]
        author_tag = root.find("{http://www.tbrc.org/models/work#}creator")
        metadata = {
            "id": f"opecha:{self.pecha_id}",
            "initial_creation_type": "ocr",
            "source_metadata": {
                "id": f"bdr:{work_id}",
                "title": converter.toUnicode(title_tag.text),
                "volume": "",
                "author": converter.toUnicode(author_tag.text) if author_tag else "",
            },
        }

        return metadata

    def create_opf(self, input_path, pecha_id):
        input_path = Path(input_path)
        self._build_dirs(input_path, id=pecha_id)

        self.dirs["release_path"] = self.dirs["opf_path"].parent / "releases"
        self.dirs["release_path"].mkdir(exist_ok=True, parents=True)

        for i, vol_path in enumerate(sorted(input_path.iterdir())):
            print(f"[INFO] Processing {input_path.name}-{vol_path.name} ...")
            base_id = f"v{i+1:03}"
            if (self.dirs["opf_path"] / "base" / f"{base_id}.txt").is_file():
                continue
            responses = self.get_input(vol_path)
            layers = self.build_layers(responses, vol_path.name, base_id)
            formatted_layers = self.format_layer(layers, base_id)
            base_text = self.get_base_text()

            # save base_text
            (self.dirs["opf_path"] / "base" / f"{base_id}.txt").write_text(base_text)

            # save layers
            vol_layer_path = self.dirs["layers_path"] / base_id
            vol_layer_path.mkdir(exist_ok=True)
            for layer, ann in formatted_layers.items():
                layer_fn = vol_layer_path / f"{layer}.yml"
                self.dump(ann, layer_fn)

        # create meta.yml
        meta_fn = self.dirs["opf_path"] / "meta.yml"
        self.dump(self.get_metadata(input_path.name), meta_fn)

        return self.dirs["opf_path"].parent


if __name__ == "__main__":
    formatter = GoogleOCRFormatter()
    formatter.create_opf("./tests/data/formatter/google_ocr/W3CN472", 300)
