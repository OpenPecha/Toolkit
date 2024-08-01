import re
from pathlib import Path
from openpecha.buda.chunker import TibetanEasyChunker, EnglishEasyChunker
from openpecha.core.layer import Layer, LayerEnum, PechaMetadata, SpanINFO
from openpecha.buda.api import get_buda_scan_info, OutlinePageLookup
import logging
import requests

class BUDAElasticSearchSerializer:
    """
    """

    def __init__(self, openpecha, get_o_graph=None, get_w_info=get_buda_scan_info):
        self.openpecha = openpecha
        self._pecha_id = openpecha.pecha_id
        self.etext_root_instance_id = f"IE0OP{self._pecha_id}"
        self.docs = []
        self.bl_volinfo = None
        self.common = None
        self.get_w_info = get_w_info
        self.get_o_graph = get_o_graph
        self.w_info = None
        self.outline_pl = None
        self.set_common()

    def add_triple(self, rdf_subject, rdf_predicate, rdf_object):
        self.lod_g.add((rdf_subject, rdf_predicate, rdf_object))

    # implementation of the API of Serialize
    def apply_layers(self):
        self.set_instance()

    def get_result(self):
        return self.docs


    """
    Entry point to build the ES doc
    """

    def meta_to_common(self):
        common = {}
        common["type"] = ["Etext"]
        common["etext_instance"] = self.etext_root_instance_id
        meta = self.openpecha.meta
        sm = meta.source_metadata
        if sm is not None:
            scanlname = sm["id"]
            if scanlname.startswith("bdr:"):
                scanlname = scanlname[4:]
            elif scanlname.startswith("http://purl.bdrc.io/resource/"):
                scanlname = scanlname[29:]
            common["etext_pagination_in"] = scanlname
        if meta.ocr_import_info is not None:
            oii = meta.ocr_import_info
            if "software_id" in oii and oii["software_id"] == "norbuketaka":
                common["etext_quality"] = 2
                # for regular ocr, we set the quality by volume
        return common

    def set_common(self):
        common = self.meta_to_common()
        if "etext_pagination_in" in common and self.get_w_info:
            self.w_info = self.get_w_info(common["etext_pagination_in"])
            mw_id = self.w_info["source_metadata"]["reproduction_of"]
            if "outline" in self.w_info["source_metadata"] and self.get_o_graph:
                outline_graph = self.get_o_graph(self.w_info["source_metadata"]["outline"])
                self.outline_pl = OutlinePageLookup(outline_graph, common["etext_pagination_in"])
            if mw_id is not None:
                common["etext_for_root_instance"] = mw_id
                common["etext_for_instance"] = mw_id # temporary, can be changed later with the outline
                common["join_field"] = { "name": "etext", "parent": mw_id }
        self.common = common

    def set_instance(self):
        for baselname, baseinfo in self.openpecha.meta.bases.items():
            self.get_base_volume(baselname, baseinfo)

    def get_ut_id(volume_basename, mw):
        if mw is None:
            return f"UT{volume_basename}"
        else:
            return f"UT{volume_basename}_{mw}"

    def get_base_volume(self, baselname, baseinfo):
        volume_string = self.openpecha.get_base(baselname)
        if len(volume_string) < 2:
            return
        volume_number = 0
        if "source_metadata" in baseinfo and "volume_number" in baseinfo["source_metadata"]:
            volume_number = baseinfo["source_metadata"]["volume_number"]
        elif "order" in baseinfo:
            volume_number = baseinfo["order"]
        else:
            volume_number = int(re.search(r"\d+", baselname).group())
        if volume_number == 0:
            # volume numbers are necessary
            logging.error("cannot find volume number")
            return
        iglname = None
        if "source_metadata" in baseinfo and "image_group_id" in baseinfo["source_metadata"]:
            iglname = baseinfo["source_metadata"]["image_group_id"]
            if iglname.startswith("bdr:"):
                iglname = iglname[4:]
            elif iglname.startswith("http://purl.bdrc.io/resource/"):
                iglname = iglname[29:]
        if iglname is None:
            for iglname_candidate, iginfo in self.w_info["image_groups"]:
                if iginfo["volume_number"] == volume_number:
                    iglname = iglname_candidate
                    break
        if iglname is None:
            logging.error("cannot find image group id")
            return
        if iglname not in self.w_info["image_groups"]:
            logging.error("cannot find image group %s" % iglname)
            return
        iginfo = self.w_info["image_groups"][iglname]
        player = self.openpecha.get_layer(baselname, LayerEnum.pagination)
        if player is None or self.outline_pl is None or len(self.outline_pl.get_mw_list(volume_number)) == 0:
            # no pagination or no outline in this volume
            doc = self.common.copy()
            volume_basename = f"{self.etext_root_instance_id}_{baselname}"
            doc["_id"] = f"UT{volume_basename}"
            doc["volumeNumber"] = volume_number
            doc["etextNumber"] = 0
            doc["etext_imagegroup"] = iglname
            doc["etext_vol"] = f"VL{volume_basename}"
            # skip first two pages
            rng = None
            if iginfo["volume_pages_bdrc_intro"] > 0 and player:
                start_cc = 0
                for annotation_id, annotation in player.annotations.items():
                    sequence = 0
                    if "imgnum" in annotation:
                        sequence = annotation["imgnum"]
                    elif "page_index" in annotation:
                        sequence = self.get_sequence(annotation["page_index"])
                    else:
                        # image numbers are necessary for this exercise
                        continue
                    # assuming that annotations are in order:
                    if sequence > iginfo["volume_pages_bdrc_intro"]:
                        start_cc = annotation["span"]["start"]
                        break
                if start_cc == 0:
                    logging.warning("character 0 found for first non-intro page, this shouldn't happen")
                else:
                    rng = (iginfo["volume_pages_bdrc_intro"], -1, start_cc, -1)
            self.set_etext_pages(doc, baselname, rng)
            self.set_etext_chunks(doc, baselname, baseinfo, rng)
            self.docs.append(doc)
            return
        has_chunks_outside_outline = False
        ranges = {}
        cur_ranges = {}
        prev_mws = set()
        ordered_mws = []
        # a range is a tuple (page_start, page_end, char_start, char_end)
        for annotation_id, annotation in player.annotations.items():
            sequence = 0
            if "imgnum" in annotation:
                sequence = annotation["imgnum"]
            elif "page_index" in annotation:
                sequence = self.get_sequence(annotation["page_index"])
            else:
                # image numbers are necessary for this exercise
                continue
            if sequence <= iginfo["volume_pages_bdrc_intro"]:
                # skip intro pages
                continue
            mws = self.outline_pl.get_mw_list(volume_number, sequence)
            # in case we have a page with OCR that has no corresponding location in the outline
            if len(mws) == 0:
                # we just add the root mw
                mws = {self.w_info["source_metadata"]["reproduction_of"]}
            # for mws that were on previous page but not this one:
            for mw in prev_mws.difference(mws):
                # we close their range
                if mw not in ranges:
                    ranges[mw] = []
                ranges[mw].append(cur_ranges[mw])
                del cur_ranges[mw]
            # for mws that were not on previous page but are on this one:
            for mw in mws.difference(prev_mws):
                if mw not in ordered_mws:
                    ordered_mws.append(mw)
                # we create a new range
                cur_ranges[mw] = (sequence, sequence, annotation["span"]["start"], annotation["span"]["end"])
            # for mws that were also on the previous page:
            for mw in mws.intersection(prev_mws):
                # we extend the range
                page_start, page_end, char_start, char_end = cur_ranges[mw]
                cur_ranges[mw] = (page_start, sequence, char_start, annotation["span"]["end"])
            prev_mws = mws
        # finish ranges
        for mw, r in cur_ranges.items():
            if mw not in ranges:
                ranges[mw] = []
            ranges[mw].append(r)
        #print(ranges)
        # then go through the ranges and add to the documents:
        for mw_i, mw in enumerate(ordered_mws):
            self.add_partial_etext_doc(mw, mw_i, baselname, iglname, baseinfo, volume_number, ranges[mw])

    def add_partial_etext_doc(self, mw, etext_in_volume, baselname, iglname, baseinfo, volume_number, ranges):
        doc = self.common.copy()
        doc["_id"] = f"UT{mw}_{baselname}"
        doc["volumeNumber"] = volume_number
        doc["etext_imagegroup"] = iglname
        doc["etext_for_instance"] = mw
        doc["etextNumber"] = etext_in_volume
        doc["etext_vol"] = f"VL{self.etext_root_instance_id}_{baselname}"
        for rng in ranges:
            self.set_etext_pages(doc, baselname, rng)
            self.set_etext_chunks(doc, baselname, baseinfo, rng)
        self.docs.append(doc)

    def set_etext_pages(self, doc, baselname, rng=None):
        player = self.openpecha.get_layer(baselname, LayerEnum.pagination)
        if player is None:
            return
        for annotation_id, annotation in player.annotations.items():
            sequence = 0
            if "imgnum" in annotation:
                sequence = annotation["imgnum"]
            elif "page_index" in annotation:
                sequence = self.get_sequence(annotation["page_index"])
            if not sequence and rng:
                continue
            if rng and (sequence < rng[0] or (rng[1] > 0 and sequence > rng[1])):
                continue
            if "etext_pages" not in doc:
                doc["etext_pages"] = []
            doc["etext_pages"].append({
                "cstart": annotation["span"]["start"],
                "cend": annotation["span"]["end"],
                "pnum": sequence
                })

    @staticmethod
    def get_sequence(page_index):
        number = int(re.search(r"\d+", page_index).group())
        return number * 2 if page_index[-1] == "b" else (number * 2) - 1

    def add_chunks(self, doc, baselname, volume_string, language, previous_i = 0, start_cc=0, end_cc=-1, rng=None):
        if rng and (end_cc != -1 or rng[3] != -1): 
            start_cc = max(start_cc, rng[2])
            if end_cc != -1 and rng[3] != -1:
                end_cc = min(rng[3], end_cc)
            else:
                end_cc = max(rng[3], end_cc)
            if end_cc <= start_cc:
                return previous_i
        chunk_indexes = self.get_chunk_indexes(volume_string, language, start_cc, end_cc)
        for i in range(0, len(chunk_indexes) - 1):
            self.set_etext_chunk(
                doc, previous_i + i, chunk_indexes[i], chunk_indexes[i + 1], baselname, volume_string, language
            )
        return previous_i + len(chunk_indexes)

    def set_etext_chunks(self, doc, baselname, baseinfo, rng=None):
        volume_string = self.openpecha.get_base(baselname)
        default_language = "bo"
        if "default_language" in baseinfo:
            default_language = baseinfo["default_language"]
        elif self.openpecha.meta.default_language is not None:
            default_language = self.openpecha.meta.default_language
        llayer = self.openpecha.get_layer(baselname, LayerEnum.language)
        if llayer is None:
            self.add_chunks(doc, baselname, volume_string, default_language, rng=rng)
        else:
            last_index = 0
            ci = 0
            # for our purpose it's crucial that the annotations are returned sorted:
            sorted_annotations = sorted(llayer.annotations.values(), key=lambda x: x["span"]["start"])
            for annotation in sorted_annotations:
                if annotation["span"]["start"] > last_index:
                    ci = self.add_chunks(doc, baselname, volume_string, default_language, ci, last_index, annotation["span"]["start"], rng=rng)
                ci = self.add_chunks(doc, baselname, volume_string, annotation["language"], ci, annotation["span"]["start"], annotation["span"]["end"], rng=rng)
                last_index = annotation["span"]["end"]
            len_vol_str = len(volume_string)
            if last_index < len_vol_str:
                self.add_chunks(doc, baselname, volume_string, default_language, ci, last_index, len_vol_str, rng=rng)

    def set_etext_chunk(self, doc, i, start_char, end_char, baselname, volume_string, language):
        if "chunks" not in doc:
            doc["chunks"] = []
        chunk = {
            "cstart": start_char,
            "cend": end_char,
        }
        chunk["text_"+language] = volume_string[start_char:end_char]
        doc["chunks"].append(chunk)

    @staticmethod
    def get_chunk_indexes(string, language, start_char = 0, end_char = 0):
        chunker = None
        if language == "bo":
            chunker = TibetanEasyChunker(string, 1500, start_char, end_char)
        else:
            chunker = EnglishEasyChunker(string, 1500, start_char, end_char)
        indexes = chunker.get_chunks()

        return indexes

