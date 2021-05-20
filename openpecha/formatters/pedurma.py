from json import encoder
import re
from pathlib import Path

import yaml

from ..utils import Vol2FnManager
from .formatter import BaseFormatter
from .layers import *
from .layers import AnnType, _attr_names

class PedurmaFormatter(BaseFormatter):
    """
    Pedurma formatter is to format preview of reconstructed pedurma.
    """

    def __init__(self, output_path, metadata):
        super().__init__(output_path, metadata)
        self.page = []
        self.durchen = []
        self.base_text = ""
    
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
        match_list = re.finditer("<.*?>", page_content)  # list of match object of given pattern in line
        for match in match_list:
            if ann.start() > match.start():
                length_before = length_before + len(match[0])
        return length_before

    def get_pages(self, vol_text):
        result = []
        pg_text = ""
        pages = re.split(r"(<p\d+-\d+>)", vol_text)
        for i, page in enumerate(pages[:-1]):
            if i % 2 == 0:
                pg_text += page
            else:
                pg_text += page
                result.append(pg_text)
                pg_text = ""
        return result

    def parse_pagination(self, walker, page_content):
        page_ann = ()
        page_pat = re.search('<p(\d+)-(\d+)>', page_content)
        page_num = page_pat.group(2)
        vol_num = page_pat.group(1)
        pat_len_before = self.search_before(page_pat, page_content)
        page_ann = {
            'page_num': page_num,
            'span':{
                'vol': vol_num,
                'start': walker,
                'end': walker + page_pat.start() - pat_len_before
            }
        }

        return page_ann

    def parse_note(self, note, walker, page_content):
        note_ann = {}
        note_pat = re.search(f'(:\S+)?{note}', page_content)
        # pat_len_before_ann = search_before(note, page_content)
        if note_pat.group(1):
            ann_start = note_pat.start() + walker 
            ann_end = ann_start + len(note_pat.group(1))
        else:
            if note_pat := re.search(f'\S+་(\S+་?){note}', page_content):
                grp_1_loc = page_content.find(note_pat.group(1))
            else:
                note_pat = re.search(f'(\S+་?){note}', page_content)
                grp_1_loc = note_pat.start()
            ann_start = grp_1_loc + walker 
            if note_pat.group(1):
                ann_end = ann_start + len(note_pat.group(1))
            else:
                ann_end = ann_start
        note_ann = {
            'span':{
                'start':ann_start,
                'end': ann_end
            },
            'note': note
        }
        page_content = re.sub(note, '', page_content, 1)
        return note_ann, page_content

    def parse_page(self, page, cur_vol_notes, cur_vol_pages, char_walker):
        page_content = page.replace('\n', '#')
        notes = re.findall(r'\<.*?\>', page_content)
        for note in notes:
            if 'p' in note:
                cur_vol_pages.append(self.parse_pagination(char_walker, page))
            else:
                note_info, page_content = self.parse_note(note, char_walker, page_content)
                cur_vol_notes.append(note_info)
        new_page = re.sub('<.*?>', '', page)

    def base_extract(self, text):
        return re.sub('<.*?>', '', text)

    def build_layers(self, text):
        char_walker = 0
        layers = {}
        cur_vol_notes = []
        cur_vol_pages = []
        pages = self.get_pages(text)
        for page in pages:
            new_page = self.parse_page(page, cur_vol_notes, cur_vol_pages, char_walker)
            char_walker += len(new_page)
        self.page.append(cur_vol_pages)
        self.durchen.append(cur_vol_notes)
        return layers
    
    def get_result(self):
        pass

    def get_base_text(self):
        base_text = self.base_text.strip()
        self.base_text = ""
        return base_text
    
    def create_opf(self, input_path, id_ = None, **kwargs):
        input_path = Path(input_path)
        self._build_dirs(input_path, id_=id_)
        self.metadata = self._load_metadata()
        vol2fn_manager = Vol2FnManager(self.metadata)

        for m_text, vol_name, n_vol in self.get_input(input_path):
            vol_id = vol2fn_manager.get_vol_id(vol_name)
            print(f"[INFO] parsing Vol {vol_name} ...")
            self.build_layers(m_text, n_vol)
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