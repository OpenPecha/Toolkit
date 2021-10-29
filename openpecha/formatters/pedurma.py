import re
from pathlib import Path

from ..utils import Vol2FnManager
from .formatter import BaseFormatter
from .layers import *
from .layers import AnnType, _attr_names


class PedurmaFormatter(BaseFormatter):
    """
    Pedurma formatter is to format preview of reconstructed pedurma.
    """

    def __init__(self, output_path=None, metadata=None):
        super().__init__(output_path, metadata)
        self.page = []
        self.durchen = []
        self.base_text = ""

    def text_preprocess(self, text):
        if text[0] == "\ufeff":
            text = text[1:]
        return text

    def _load_metadata(self):
        if self.metadata:
            return self.metadata
        meta_fn = self.dirs["opf_path"] / "meta.yml"
        if meta_fn.is_file():
            return self.load(meta_fn)
        else:
            return {}

    def _save_metadata(self, **kwargs):
        meta_fn = self.dirs["opf_path"] / "meta.yml"
        if kwargs:
            self.metadata.update(kwargs)
        if "id" not in self.metadata:
            self.metadata["id"] = f"opecha:{self.pecha_path.name}"
        self.dump(self.metadata, meta_fn)

    def get_input(self, input_path):
        fns = list(input_path.iterdir())
        fns_len = len(fns)
        for fn in sorted(fns):
            yield self.text_preprocess(fn.read_text()), fn.name, fns_len

    def search_before(self, ann, page_content):
        length_before = 0
        match_list = re.finditer(
            "<.*?>", page_content
        )  # list of match object of given pattern in line
        for match in match_list:
            if ann.start() > match.start():
                length_before = length_before + len(match[0])
        return length_before

    def get_pages(self, vol_text):
        result = []
        pg_text = ""
        pages = re.split(r"(〔[𰵀-󴉱]?\d+〕)", vol_text)
        for i, page in enumerate(pages[1:]):
            if i % 2 == 0:
                pg_text += page
            else:
                pg_text += page
                result.append(pg_text)
                pg_text = ""
        return result

    def parse_pagination(self, walker, base_page, page_content):
        page_ann = {}
        page_pat = re.search(r"〔[𰵀-󴉱]?(\d+)〕", page_content)
        imgnum = page_pat.group(1)
        start_page = walker + 1
        end_page = start_page + len(base_page) - 2
        span = Span(start_page, end_page)
        page_ann = Page(span, imgnum=imgnum)
        return page_ann

    def get_pub_wise_note(self, note):
        reformat_notes = {"«པེ་»": "", "«སྣར་»": "", "«སྡེ»": "", "«ཅོ་»": ""}
        note_parts = re.split("(«.+?»)", note)
        pubs = note_parts[1::2]
        notes = note_parts[2::2]
        for walker, (pub, note_part) in enumerate(zip(pubs, notes)):
            if note_part:
                reformat_notes[pub] = note_part.replace(">", "")
            else:
                if notes[walker + 1]:
                    reformat_notes[pub] = notes[walker + 1].replace(">", "")
                else:
                    reformat_notes[pub] = notes[walker + 2].replace(">", "")

        return reformat_notes

    def parse_note(self, note, walker, page_content):
        page_content = re.sub(r"〔[𰵀-󴉱]?\d+〕", "", page_content)
        note_ann = {}
        note_pat = re.search(rf"(:\S+)?{note}", page_content)
        if note_pat.group(1):
            ann_start = note_pat.start() + walker
            ann_end = ann_start + len(note_pat.group(1))
        else:
            if re.search(rf"\S+་([^#]\S+་?){note}", page_content):
                note_pat = re.search(rf"\S+་([^#]\S+་?){note}", page_content)
                grp_1_loc = page_content.find(note_pat.group(1))
            else:
                note_pat = re.search(rf"([^#]\S+་?){note}", page_content)
                grp_1_loc = note_pat.start()
            ann_start = grp_1_loc + walker
            if note_pat.group(1):
                ann_end = ann_start + len(note_pat.group(1))
            else:
                ann_end = ann_start
        note_ann = {
            "span": {
                "start": ann_start,  # the variant unit or variant location is capture with help of this span
                "end": ann_end - 1,
            },
            "variants": self.get_pub_wise_note(note),
            "collation_note": note,
        }
        page_content = re.sub(note, "", page_content, 1)
        return note_ann, page_content

    def parse_page(self, page, cur_vol_notes, cur_vol_pages, char_walker):
        page_content = page.replace("\n", "#")
        notes = re.findall(r"\<.*?\>", page_content)
        for note in notes:
            note_info, page_content = self.parse_note(note, char_walker, page_content)
            cur_vol_notes.append(("", note_info))
        new_page = self.base_extract(page)
        page_ann = self.parse_pagination(char_walker, new_page, page)
        cur_vol_pages.append(("", page_ann))
        return new_page

    def base_extract(self, text):
        text = re.sub(r"〔[𰵀-󴉱]?\d+〕", "", text)
        return re.sub("<.*?>", "", text)

    def build_layers(self, text):
        char_walker = 0
        cur_vol_notes = []
        cur_vol_pages = []
        pages = self.get_pages(text)
        for page in pages:
            new_page = self.parse_page(page, cur_vol_notes, cur_vol_pages, char_walker)
            char_walker += len(new_page)
        self.page.append(cur_vol_pages)
        self.durchen.append(cur_vol_notes)
        self.base_text = self.base_extract(text)

    def get_result(self):
        result = {
            AnnType.topic: [],
            AnnType.sub_topic: [],
            AnnType.pagination: self.page,
            AnnType.pedurma_note: self.durchen,
        }
        return result

    def get_base_text(self):
        base_text = self.base_text
        self.base_text = ""
        return base_text

    def create_opf(self, input_path, id_=None, **kwargs):
        input_path = Path(input_path)
        self._build_dirs(input_path, id_=id_)
        self.metadata = self._load_metadata()
        vol2fn_manager = Vol2FnManager(self.metadata)

        for m_text, vol_name, n_vol in self.get_input(input_path):
            vol_id = vol2fn_manager.get_vol_id(vol_name)
            print(f"[INFO] parsing Vol {vol_name} ...")
            self.build_layers(m_text)
            if "is_text" in kwargs:
                if kwargs["is_text"]:
                    continue

            base_text = self.get_base_text()
            (self.dirs["opf_path"] / "base" / f"{vol_id}.txt").write_text(base_text)

        # save pecha layers
        layers = self.get_result()
        for vol_layers, vol_id in self.format_layer(layers):
            if vol_id:
                print(f"[INFO] Creating layers for {vol_id} ...")
                vol_layer_path = self.dirs["layers_path"] / vol_id
                vol_layer_path.mkdir(exist_ok=True)
            else:
                print("[INFO] Creating index layer for Pecha ...")

            for layer, ann in vol_layers.items():
                if layer == "index":
                    layer_fn = self.dirs["opf_path"] / f"{layer}.yml"
                else:
                    layer_fn = vol_layer_path / f"{layer}.yml"
                self.dump(ann, layer_fn)

        self._save_metadata(vol2fn=dict(vol2fn_manager.vol2fn))
