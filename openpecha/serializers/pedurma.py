import re
from pathlib import Path

import yaml

from openpecha.formatters.layers import AnnType

from .serialize import Serialize


class PedurmaSerializer(Serialize):
    """Pedurma serializer class to get diplomatic text."""

    def __get_adapted_span(self, span, vol_id):
        """Adapts the annotation span to base-text of the text

        Adapts the annotation span, which is based on volume base-text
        to text base-text.

        Args:
            span (dict): span of a annotation, eg: {start:, end:}
            vol_id (str): id of vol, where part of the text exists.

        Returns:
            adapted_start (int): adapted start based on text base-text
            adapted_end (int): adapted end based on text base-text

        """
        adapted_start = span["start"] - self.text_spans[vol_id]["start"]
        adapted_end = span["end"] - self.text_spans[vol_id]["start"]
        return adapted_start, adapted_end

    def get_local_id(self, ann, uuid2localid):
        try:
            return chr(uuid2localid[ann["id"]])
        except Exception:
            return ""

    def apply_annotation(self, vol_id, ann, uuid2localid):
        """Applies annotation to specific volume base-text, where part of the text exists.

        Args:
            vol_id (str): id of vol, where part of the text exists.
            ann (dict): annotation of any type.

        Returns:
            None

        """
        only_start_ann = False
        start_payload = "("
        end_payload = ")"
        side = "ab"
        local_id = self.get_local_id(ann, uuid2localid)
        if ann["type"] == AnnType.pagination:
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
        elif ann["type"] == AnnType.pedurma_note:
            start_payload = ""
            end_payload = f'{ann["collation_note"]}'

        start_cc, end_cc = self.__get_adapted_span(ann["span"], vol_id)
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)

    def get_chunks(self, text):
        """Break the text on where notes are located

        Args:
            text (text): preview text

        Returns:
            list: contain all the chunks and note along with it
        """
        result = []
        cur_note = []
        chunks = re.split(r"(\<.+?\>)", text)
        for chunk in chunks:
            if "{" in chunk:
                note = yaml.safe_load(chunk)
                cur_note.append(note)
                result.append(cur_note)
                cur_note = []
            else:
                cur_note.append(chunk)
        result.append([chunk, {}])
        return result

    def process_chunk(self, chunk, pub):
        """Reinsert the note to chunk according to publication selected

        Args:
            chunk (list): text chunk and its notes
            pub (str): publication annotation

        Returns:
            str: chunk text with note added according to publication
        """
        chunk_text = chunk[0]
        chunk_notes = chunk[1]
        if chunk_notes:
            note = chunk_notes[pub]
            if note:
                old_note = re.search(r"(:\S+)\n?", chunk_text).group(1)
                chunk_text = re.sub(old_note, note, chunk_text)
            else:
                chunk_text = re.sub(":", "", chunk_text)
        return chunk_text

    def get_diplomatic_text(self, text, pub):
        """Reinsert the notes from pedurma of given publication and generates version of the text of given publication

        Args:
            text (str): text with pedurma notes of all other publication
            pub (str): annotation of publication de for derge, pe for pecing, nar for narthang and co for cone

        Returns:
            str: Text of mentioned publication extracted from pedurma text
        """
        diplomatic_text = ""
        chunks = self.get_chunks(text)
        for chunk in chunks:
            diplomatic_text += self.process_chunk(chunk, pub)
        return diplomatic_text

    def serialize(self, output_path="./output/diplomatic_text/", pub="pe"):
        """Serialize pedurma preview opf to diplomatic text of given publication

        Args:
            output_path (str, optional): output path where user wants to save the diplomatic text. Defaults to "./output/diplomatic_text/".
            pub (str, optional): publication annotation . Defaults to 'pe'.
        """
        output_path = Path(output_path)
        self.apply_layers()
        results = self.get_result()
        for vol_id, result in results.items():
            # diplomatic_text = self.get_diplomatic_text(result, pub)
            (output_path / vol_id).write_text(result, encoding="utf-8")
        print("Serialize complete...")
