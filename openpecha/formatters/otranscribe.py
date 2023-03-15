import re

from pathlib import Path
from openpecha.core.annotations import TranscriptionTimeSpan, Span
from openpecha.formatters.formatter import BaseFormatter
from openpecha.core.layer import TranscriptionTimeSpanLayer, LayerEnum
from openpecha.core.annotations import TranscriptionTimeSpan, Span
from openpecha.core.pecha import OpenPechaFS
from openpecha.core.ids import get_initial_pecha_id, get_base_id
from openpecha.core.metadata import InitialPechaMetadata
import json
from bs4 import BeautifulSoup


def get_json_from_str(text):
    otr_json = json.loads(text)
    return otr_json


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup


def get_all_timestamps(soup):
    return soup.findAll("span", {"class": "timestamp"})


def get_text_between(start, end):
    text = ""
    tag = start.next_element.next_element
    while tag != end:
        if tag.name is None:
            text += tag.text
        tag = tag.next_element
    return text


class OTranscribeFormatter(BaseFormatter):
    """
    oTranscribe formatter for .otr file.
    """

    def __init__(
        self,
        output_path="./output",
        metadata=None,
        media_url=None,
        time_unit="microsecond",
    ):
        super().__init__(output_path, metadata)
        self.media_url = media_url
        self.time_unit = time_unit

    def text_preprocess(self, text):
        otr_json = get_json_from_str(text)
        return otr_json["text"].strip()

    def build_layers(self, text):
        transcription_time_span_layer = TranscriptionTimeSpanLayer(
            media_url=self.media_url,
            time_unit=self.time_unit,
        )

        soup = parse_html(text)
        timestamps = get_all_timestamps(soup)
        base_text = ""
        char_walker = 0
        for start, end in zip(timestamps, timestamps[1:]):
            time_start = float(start["data-timestamp"]) * 10**6
            time_end = float(end["data-timestamp"]) * 10**6
            time_span = Span(start=time_start, end=time_end)
            text_between = get_text_between(start, end).strip()
            text_end = char_walker + len(text_between)
            text_span = Span(start=char_walker, end=text_end)
            char_walker += len(text_between) + 1
            transcription_time_span_layer.set_annotation(
                TranscriptionTimeSpan(span=text_span, time_span=time_span)
            )
            base_text += text_between + "\n"
        # \xa0 is non-breaking space. Replace it with space.
        base_text = base_text.replace("\xa0", " ")
        return {
            LayerEnum.transcription_time_span: transcription_time_span_layer
        }, base_text

    def create_opf_from_dir(self, input_path):
        input_path = Path(input_path)
        if not input_path.is_dir():
            raise TypeError("Only directories are allowed")
        if not len(list(input_path.glob("*.otr"))):
            raise Exception("No .otr file found")

        pecha_id = get_initial_pecha_id()
        pecha_path = self.output_path / f"{pecha_id}/{pecha_id}.opf"
        pecha_meta = InitialPechaMetadata(id=pecha_id)
        pecha = OpenPechaFS(path=pecha_path, pecha_id=pecha_id)
        pecha._meta = pecha_meta

        for otr_file in input_path.glob("*.otr"):
            m_text = self.get_input(otr_file)
            layers, base_text = self.build_layers(m_text)

            base_id = get_base_id()

            pecha.set_base(
                content=base_text,
                base_name=base_id,
                metadata={
                    "source_metadata": {
                        "title": "test",
                        "author": "sonam",
                        "id": pecha_id,
                    },
                    "base_file": f"{base_id}.txt",
                },
            )
            pecha.set_layer(
                base_name=base_id, layer=layers[LayerEnum.transcription_time_span]
            )
        return pecha

    def create_opf(self, input_path):
        input_path = Path(input_path)
        if input_path.is_dir():
            return self.create_opf_from_dir(input_path)
        pecha_id = get_initial_pecha_id()
        m_text = self.get_input(input_path)
        layers, base_text = self.build_layers(m_text)
        pecha_path = self.output_path / f"{pecha_id}/{pecha_id}.opf"
        pecha_meta = InitialPechaMetadata(id=pecha_id)
        pecha = OpenPechaFS(path=pecha_path, pecha_id=pecha_id)
        base_id = get_base_id()

        pecha._meta = pecha_meta
        pecha.set_base(
            content=base_text,
            base_name=base_id,
            metadata={
                "source_metadata": {"title": "test", "author": "sonam", "id": pecha_id},
                "base_file": f"{base_id}.txt",
            },
        )
        pecha.set_layer(
            base_name=base_id, layer=layers[LayerEnum.transcription_time_span]
        )
        return pecha
