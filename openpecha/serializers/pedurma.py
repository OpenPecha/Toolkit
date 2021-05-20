import os
import re
import shutil
import zipfile
from bs4 import BeautifulSoup
from pathlib import Path

import requests
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
        if ann["type"] == AnnType.pagination:
            start_payload = ''
            end_payload = f'<p{ann["span"]["vol"]}-{ann["page_num"]}>'
        elif ann["type"] == AnnType.pedurma_note:
            start_payload = "("
            end_payload = f',{ann["note"]})'
        

        start_cc, end_cc = self.__get_adapted_span(ann["span"], vol_id)
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)


    def serialize(self, output_path="./output/diplomatic_text/"):
        output_path = Path(output_path)
        self.apply_layers()
        results = self.get_result()
        for vol_id, result in results.items():
            (output_path / vol_id).write_text(result, encoding='utf-8')
        print('Serialize complete...')