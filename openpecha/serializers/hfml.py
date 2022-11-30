from pathlib import Path

from openpecha.formatters.layers import LayerEnum
from openpecha.utils import Vol2FnManager
from openpecha.serializers.serialize import Serialize


class HFMLSerializer(Serialize):
    """
    HFML (Human Friendly Markup Language) serializer class for OpenPecha.
    """

    def get_local_id(self, ann, uuid2localid):
        try:
            return chr(uuid2localid[ann["id"]])
        except Exception:
            return ""

    def apply_annotation(self, base_id, ann, uuid2localid=None):
        only_start_ann = False
        start_payload = "("
        end_payload = ")"
        side = "ab"
        local_id = self.get_local_id(ann, uuid2localid)
        ann_type = LayerEnum(ann["type"])
        if ann_type == LayerEnum.pagination:
            pg_idx = ann.get("page_index", "")
            if not pg_idx:
                pg_idx = ann.get("imgnum", "")
            if pg_idx == "0b":
                pg_n = ann["reference"][5:-1]
                pg_side = ann["reference"][-1]
                if "-" in pg_n:
                    pg_n = int(pg_n.split("-")[0])
                    pg_side = side[int(pg_side)]
                    start_payload = f"[{local_id}{pg_n}{pg_side}]"
                else:
                    pg_n = int(pg_n)
                    if pg_side.isdigit():
                        pg_n = str(pg_n) + pg_side
                        pg_side = ""
                    start_payload = f"〔{local_id}{pg_n}{pg_side}〕"
            else:
                start_payload = f"〔{local_id}{pg_idx}〕"
            if ann.get("reference", ""):
                start_payload += f' {ann["reference"]}\n'
            else:
                start_payload += "\n"
            only_start_ann = True
        elif ann_type == LayerEnum.topic:
            start_payload = f"{{{ann['work_id']}}}"
            only_start_ann = True
        elif ann_type == LayerEnum.sub_topic:
            start_payload = f"{{{ann['work_id']}}}"
            only_start_ann = True
        elif ann_type == LayerEnum.correction:
            start_payload = f"<{local_id}"
            end_payload = f',{ann["correction"]}>'
        elif ann_type == LayerEnum.archaic:
            start_payload = f"{{{local_id}"
            end_payload = f',{ann["modern"]}}}'
        elif ann_type == LayerEnum.peydurma:
            start_payload = f"#{local_id}"
            only_start_ann = True
        elif ann_type == LayerEnum.error_candidate:
            start_payload = f"[{local_id}"
            end_payload = "]"
        elif ann_type == LayerEnum.book_title:
            start_payload = f"<{local_id}k1"
            end_payload = ">"
        elif ann_type == LayerEnum.book_number:
            start_payload = f"<{local_id}k4"
            end_payload = ">"
        elif ann_type == LayerEnum.poti_title:
            start_payload = f"<{local_id}k2"
            end_payload = ">"
        elif ann_type == LayerEnum.author:
            start_payload = f"<{local_id}au"
            end_payload = ">"
        elif ann_type == LayerEnum.chapter:
            start_payload = f"<{local_id}k3"
            end_payload = ">"
        elif ann_type == LayerEnum.tsawa:
            start_payload = f"<{local_id}m"
            end_payload = "m>"
        elif ann_type == LayerEnum.citation:
            start_payload = f"<{local_id}g"
            end_payload = "g>"
        elif ann_type == LayerEnum.sabche:
            start_payload = f"<{local_id}q"
            end_payload = "q>"
        elif ann_type == LayerEnum.yigchung:
            start_payload = f"<{local_id}y"
            end_payload = "y>"
        elif ann_type == LayerEnum.durchen:
            start_payload = f"<{local_id}d"
            end_payload = "d>"

        start_cc, end_cc = self._get_adapted_span(ann["span"], base_id)
        # start_cc -= 4
        self.add_chars(base_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(base_id, end_cc, False, end_payload)

    def serialize(self, output_path="./output/publication", text_id=""):
        pecha_id = self.opf_path.stem
        self.apply_layers()
        results = self.get_result()
        vol2fn_manager = Vol2FnManager(self.get_meta_data())
        output_path = Path(output_path) / pecha_id
        output_path.mkdir(exist_ok=True, parents=True)
        print("[INFO] Creating HFML view")
        for base_id, hfml_text in results.items():
            fn = vol2fn_manager.get_fn(base_id) + text_id
            try:
                vol_hfml_fn = output_path / fn
            except Exception:
                vol_hfml_fn = output_path / base_id
            print(f"[INFO]\t- saving {fn}")
            vol_hfml_fn.write_text(hfml_text)
