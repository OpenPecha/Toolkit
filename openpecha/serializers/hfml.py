from pathlib import Path

from openpecha.formatters.layers import AnnType

from .serialize import Serialize


class SerializeHFML(Serialize):
    """
    HFML (Human Friendly Markup Language) serializer class for OpenPecha.
    """

    def get_local_id(self, ann, uuid2localid):
        try:
            return chr(uuid2localid[ann["id"]])
        except Exception:
            return ""

    def apply_annotation(self, vol_id, ann, uuid2localid):
        only_start_ann = False
        start_payload = "("
        end_payload = ")"
        side = "ab"
        local_id = self.get_local_id(ann, uuid2localid)
        if ann["type"] == AnnType.pagination:
            if ann["page_index"] == "0b":
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
                    start_payload = f"[{local_id}{pg_n}{pg_side}]"
            else:
                start_payload = f'[{local_id}{ann["page_index"]}]'

            if ann["page_info"]:
                start_payload += f' {ann["page_info"]}\n'
            # elif ann["reference"]:
            #     start_payload += f' {ann["reference"]}\n'
            else:
                start_payload += "\n"
            only_start_ann = True
        elif ann["type"] == AnnType.correction:
            start_payload = f"<{local_id}"
            end_payload = f',{ann["correction"]}>'
        elif ann["type"] == AnnType.peydurma:
            start_payload = f"#{local_id}"
            only_start_ann = True
        elif ann["type"] == AnnType.error_candidate:
            start_payload = f"[{local_id}"
            end_payload = "]"
        elif ann["type"] == AnnType.book_title:
            start_payload = f"({local_id}k1"
            end_payload = ")"
        elif ann["type"] == AnnType.poti_title:
            start_payload = f"({local_id}k2"
            end_payload = ")"
        elif ann["type"] == AnnType.author:
            start_payload = f"({local_id}au"
            end_payload = ")"
        elif ann["type"] == AnnType.chapter:
            start_payload = f"({local_id}k3"
            end_payload = ")"
        elif ann["type"] == AnnType.tsawa:
            start_payload = f"<{local_id}m"
            end_payload = "m>"
        elif ann["type"] == AnnType.citation:
            start_payload = f"<{local_id}g"
            end_payload = "g>"
        elif ann["type"] == AnnType.sabche:
            start_payload = f"<{local_id}q"
            end_payload = "q>"
        elif ann["type"] == AnnType.yigchung:
            start_payload = f"<{local_id}y"
            end_payload = "y>"

        start_cc, end_cc = self._get_adapted_span(ann["span"], vol_id)
        # start_cc -= 4
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)

    def serialize(self, output_path="./output/publication"):
        pecha_id = self.opfpath.stem
        self.apply_layers()
        results = self.get_result()
        output_path = Path(output_path) / pecha_id
        output_path.mkdir(exist_ok=True, parents=True)
        for vol_id, hfml_text in results.items():
            vol_hfml_fn = output_path / f"{vol_id}.txt"
            print(f"[INFO] saving {vol_id} hfml text")
            vol_hfml_fn.write_text(hfml_text)
