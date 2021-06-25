import gzip
import json
import math
import re
from pathlib import Path

import requests

from openpecha.core.annotation import Page, Span
from openpecha.core.layer import Layer, LayerEnum
from openpecha.formatters import BaseFormatter
from openpecha.utils import gzip_str, dump_yaml


class GoogleOCRFormatter(BaseFormatter):
    """
    OpenPecha Formatter for Google OCR JSON output of scanned pecha.
    """

    def __init__(self, output_path=None, metadata=None):
        super().__init__(output_path, metadata)
        self.n_page_breaker_char = 3
        self.page_break = "\n" * self.n_page_breaker_char
        self.base_text = []
        self.vols_meta = {}

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
                if fn.suffix == ".gz":
                    yield json.load(gzip.open(str(fn), "rb")), fn.stem.split(".")[0]
                else:
                    yield json.load(fn.open()), fn.stem
            except GeneratorExit:
                return None, None
            except Exception:
                yield None, None

    def format_layer(self, layers, base_id):
        anns = {}
        for (start, end, n_pg), page_ref in zip(layers["pages"], layers["pages_ref"]):
            uuid = self.get_unique_id()
            span = Span(start=start, end=end)
            page = Page(span=span, imgnum=n_pg, reference=page_ref)
            anns[uuid] = page

        layer = Layer(annotation_type=LayerEnum("Pagination"), annotations=anns)
        result = {
            LayerEnum("Pagination").value: json.loads(layer.json(exclude_none=True))
        }

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

    def _get_lines(self, text, last_pg_end_idx, is_first_pg):
        lines = []
        line_breaks = [m.start() for m in re.finditer("\n", text)]

        start = last_pg_end_idx

        # increase the start idx with page_breaker_char for page greater than frist page.
        if not is_first_pg:
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

    @staticmethod
    def _get_imagelist_meta(vol_name):
        r = requests.get(f"http://iiifpres.bdrc.io/il/v:bdr:{vol_name}")
        img2seq = {}
        for i, img in enumerate(r.json(), start=1):
            name, ext = img["filename"].split(".")
            img2seq[name] = {"num": i, "ext": ext}
        return img2seq

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
        img2seq = self._get_imagelist_meta(vol_name)
        for response, page_ref in responses:
            n_pg = img2seq[page_ref]["num"]

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
            pages_ref.append(f"{page_ref}.{img2seq[page_ref]['ext']}")

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
                "id": self.pecha_id,
                "initial_creation_type": "ocr",
                "source_metadata": {
                    "id": f"{work_id}",
                    "title": "",
                    "author": "",
                    "volume": {},
                },
            }
            return metadata

        title_tag = root[0]
        author_tag = root.find("{http://www.tbrc.org/models/work#}creator")
        metadata = {
            "id": self.pecha_id,
            "initial_creation_type": "ocr",
            "source_metadata": {
                "id": f"bdr:{work_id}",
                "title": converter.toUnicode(title_tag.text),
                "volumes": self.vols_meta,
                "author": converter.toUnicode(author_tag.text) if author_tag else "",
            },
        }

        return metadata

    def set_vols_meta(self, src_vol_id, base_file_name):
        self.vols_meta[self.get_unique_id()] = {
            "image_group_id": src_vol_id,
            "title": "",
            "base_file": base_file_name,
        }

    def create_opf(self, input_path, pecha_id):
        input_path = Path(input_path)
        self._build_dirs(input_path, id_=pecha_id)

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
                dump_yaml(ann, layer_fn)

            self.set_vols_meta(vol_path.name, f"{base_id}.txt")

        # create meta.yml
        meta_fn = self.dirs["opf_path"] / "meta.yml"
        dump_yaml(self.get_metadata(input_path.name), meta_fn)

        return self.dirs["opf_path"].parent


if __name__ == "__main__":
    formatter = GoogleOCRFormatter()
    formatter.create_opf("../../Esukhia/img2opf/archive/output/W1PD95844", 300)
