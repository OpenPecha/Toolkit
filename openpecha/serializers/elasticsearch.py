import re
from pathlib import Path
from openpecha.buda.chunker import TibetanEasyChunker, EnglishEasyChunker
from openpecha.core.layer import Layer, LayerEnum, PechaMetadata, SpanINFO
import logging
import requests

class BUDAElasticSearchSerializer:
    """
    """

    def __init__(self, openpecha, offline=False):
        self.openpecha = openpecha
        self._pecha_id = openpecha.pecha_id
        self.etext_root_instance_id = f"IE0OP{self._pecha_id}"
        self.docs = []
        self.bl_volinfo = None
        self.common = None
        self.offline = offline


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
        common["etext_for_root_instance_id"] = self.etext_root_instance_id
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

    def get_doc_for_w(self, w_id):
        """
        Get the MW (instance) document in the database that corresponds to a W (scans)
        """
        if self.offline:
            return None, None
        query = {
            "query": {
                "term": {
                    "merged.keyword": w_id
                }
            }
        }
        response = requests.post(f"https://autocomplete.bdrc.io/search", json=query)
        if response.status_code == 200:
            results = response.json()
            hits = results.get('hits', {}).get('hits', [])
            if not hits:
                logging.error("No documents found for "+w_id)
                return None, None
            if len(hits) > 1:
                logging.error("More than one document found for "+w_id)
            return hits[0]['_id'], hits[0]['_source']
        else:
            logging.error(f"Error querying Elasticsearch: {response.status_code} {response.text}")
            return None, None

    def get_common(self):
        if self.common is not None:
            return self.common
        common = self.meta_to_common()
        if "etext_pagination_in" in common:
            mw_id, mw_doc = self.get_doc_for_w(common["etext_pagination_in"])
            if mw_id is not None:
                common["etext_for_root_instance_id"] = mw_id
                common["etext_for_instance_id"] = mw_id # temporary, can be changed later with the outline
                if "pop_score" in mw_doc:
                    common["etext_instance_pop_score"] = mw_doc["pop_score"]
                for field in [
                        "db_score",
                        "firstScanSyncDate",
                        "inCollection",
                        "associatedTradition",
                        "associatedCentury",
                        "ric",
                        "scans_access",
                        "scans_quality",
                        "scans_freshness",
                        #"etext_access",
                        "workGenre",
                        "workIsAbout",
                        "author",
                        "translator",
                        "complete",
                        "seriesName_res",
                        "authorshipStatement_bo_x_ewts",
                        "authorshipStatement_en",
                        "publisherLocation_bo_x_ewts",
                        "publisherName_en",
                        "publisherLocation_en",
                        "prefLabel_bo_x_ewts",
                        "prefLabel_en"
                        ]:
                    if field in mw_doc:
                        common[field] = mw_doc[field]
                for field in [
                        "authorshipStatement_bo_x_ewts",
                        "authorshipStatement_en",
                        "publisherLocation_bo_x_ewts",
                        "publisherName_en",
                        "publisherLocation_en",
                        "prefLabel_bo_x_ewts",
                        "prefLabel_en"
                        ]:
                    if field in mw_doc:
                        common["etext_"+field] = mw_doc[field]
        self.common = common
        return self.common

    def set_instance(self):
        for baselname, baseinfo in self.openpecha.meta.bases.items():
            self.get_base_volume(baselname, baseinfo)

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
        doc = self.get_common()
        volume_basename = f"{self.etext_root_instance_id}_{baselname}"
        doc["_id"] = f"UT{volume_basename}"
        doc["volumeNumber"] = volume_number
        doc["etextNumber"] = 0
        doc["etext_vol_id"] = f"VL{volume_basename}"
        self.set_etext(doc, baselname, baseinfo, volume_number)
        self.docs.append(doc)

    def set_etext(self, doc, baselname, baseinfo, volume_number):
        volume_basename = f"{self.etext_root_instance_id}_{baselname}"
        if "source_metadata" in baseinfo and "image_group_id" in baseinfo["source_metadata"]:
            iglname = baseinfo["source_metadata"]["image_group_id"]
            if iglname.startswith("bdr:"):
                iglname = iglname[4:]
            elif iglname.startswith("http://purl.bdrc.io/resource/"):
                iglname = iglname[29:]
            doc["etext_imagegroup_id"] = iglname
        self.set_etext_pages(doc, baselname)
        self.set_etext_chunks(doc, baselname, baseinfo)

    def set_etext_pages(self, doc, baselname):
        player = self.openpecha.get_layer(baselname, LayerEnum.pagination)
        if player is None:
            return
        for annotation_id, annotation in player.annotations.items():
            self.set_etext_page(doc, annotation_id, annotation, baselname)

    def set_etext_page(self, doc, annotation_id, annotation, volume_name):
        sequence = 0
        if "imgnum" in annotation:
            sequence = annotation["imgnum"]
        elif "page_index" in annotation:
            sequence = self.get_sequence(annotation["page_index"])
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


    def add_chunks(self, doc, baselname, volume_string, language, previous_i = 0, start_cc=0, end_cc=-1):
        chunk_indexes = self.get_chunk_indexes(volume_string, language, start_cc, end_cc)
        for i in range(0, len(chunk_indexes) - 1):
            self.set_etext_chunk(
                doc, previous_i + i, chunk_indexes[i], chunk_indexes[i + 1], baselname, volume_string, language
            )
        return previous_i + len(chunk_indexes)


    def set_etext_chunks(self, doc, baselname, baseinfo):
        volume_string = self.openpecha.get_base(baselname)
        default_language = "bo"
        if "default_language" in baseinfo:
            default_language = baseinfo["default_language"]
        elif self.openpecha.meta.default_language is not None:
            default_language = self.openpecha.meta.default_language
        llayer = self.openpecha.get_layer(baselname, LayerEnum.language)
        if llayer is None:
            self.add_chunks(doc, baselname, volume_string, default_language)
        else:
            last_index = 0
            ci = 0
            # for our purpose it's crucial that the annotations are returned sorted:
            sorted_annotations = sorted(llayer.annotations.values(), key=lambda x: x["span"]["start"])
            for annotation in sorted_annotations:
                if annotation["span"]["start"] > last_index:
                    ci = self.add_chunks(doc, baselname, volume_string, default_language, ci, last_index, annotation["span"]["start"])
                ci = self.add_chunks(doc, baselname, volume_string, annotation["language"], ci, annotation["span"]["start"], annotation["span"]["end"])
                last_index = annotation["span"]["end"]
            len_vol_str = len(volume_string)
            if last_index < len_vol_str:
                self.add_chunks(doc, baselname, volume_string, default_language, ci, last_index, len_vol_str)

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

