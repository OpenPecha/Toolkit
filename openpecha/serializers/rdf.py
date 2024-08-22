import re
from pathlib import Path
import rdflib
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD, Namespace, NamespaceManager
from openpecha.buda.chunker import TibetanEasyChunker, EnglishEasyChunker
from openpecha.core.layer import Layer, LayerEnum, PechaMetadata, SpanINFO
from openpecha.buda.api import get_buda_scan_info, OutlinePageLookup

rdf = RDF
rdfs = RDFS
bdr = Namespace("http://purl.bdrc.io/resource/")
bdo = Namespace("http://purl.bdrc.io/ontology/core/")
bdg = Namespace("http://purl.bdrc.io/graph/")
bda = Namespace("http://purl.bdrc.io/admindata/")
adm = Namespace("http://purl.bdrc.io/ontology/admin/")

nsm = NamespaceManager(rdflib.Graph())
nsm.bind("bdr", bdr)
nsm.bind("", bdo)
nsm.bind("bdg", bdg)
nsm.bind("bda", bda)
nsm.bind("adm", adm)
nsm.bind("rdf", rdf)
nsm.bind("rdfs", rdfs)

def to_lname(uri):
    if uri.startswith("bdr:"):
        return uri[4:]
    elif uri.startswith("http://purl.bdrc.io/resource/"):
        return uri[29:]
    return uri

class BUDARDFSerializer:
    """
    """

    def __init__(self, openpecha, include_contents=False, get_o_graph=None, get_w_info=get_buda_scan_info):

        self.openpecha = openpecha
        self._pecha_id = openpecha.pecha_id
        self.lname = f"IE0OP{self._pecha_id}"
        self.graph_r = bdg[self.lname]
        self.lod_ds = rdflib.Dataset()
        self.lod_g = self.lod_ds.graph(self.graph_r)
        self.lod_g.namespace_manager = nsm
        self.bl_volinfo = None
        self.include_contents = include_contents
        self.get_o_graph = get_o_graph
        self.get_w_info = get_w_info
        self.outline_pl = None

    def add_triple(self, rdf_subject, rdf_predicate, rdf_object):
        self.lod_g.add((rdf_subject, rdf_predicate, rdf_object))

    # implementation of the API of Serialize
    def apply_layers(self):
        self.set_instance()

    def get_result(self):
        return self.lod_g

    """
    Entry point to build the RDF graph
    """

    def set_instance(self):
        self.add_triple(bdr[f"{self.lname}"], rdf.type, bdo["EtextInstance"])
        meta = self.openpecha.meta
        sm = meta.source_metadata
        if sm is not None:
            scanlname = to_lname(sm["id"])
            self.add_triple(
                bdr[self.lname], bdo["instanceReproductionOf"], bdr[scanlname]
            )
            self.add_triple(
                bdr[scanlname], bdo["instanceHasReproduction"], bdr[self.lname]
            )
            if self.get_w_info:
                self.w_info = self.get_w_info(scanlname)
                self.mw_lname = to_lname(self.w_info["source_metadata"]["reproduction_of"])
                if "outline" in self.w_info["source_metadata"] and self.get_o_graph:
                    outline_graph = self.get_o_graph(self.w_info["source_metadata"]["outline"])
                    self.outline_pl = OutlinePageLookup(outline_graph, scanlname, self.w_info)
        if meta.initial_creation_type == "ocr":
            self.add_triple(
                bdr[self.lname], bdo["contentMethod"], bdr['ContentMethod_OCR']
            )
        if meta.statistics is not None:
            if "ocr_word_median_confidence_index" in meta.statistics:
                self.add_triple(
                    bdr[self.lname], bdo["OPFOCRWordMedianConfidenceIndex"], Literal(meta.statistics["ocr_word_median_confidence_index"], datatype=XSD.float)
                )
            if "ocr_word_mean_confidence_index" in meta.statistics:
                self.add_triple(
                    bdr[self.lname], bdo["OPFOCRWordMeanConfidenceIndex"], Literal(meta.statistics["ocr_word_mean_confidence_index"], datatype=XSD.float)
                )
        if meta.legacy_id is not None and meta.legacy_id:
            legacylname = f"IE0OP{meta.legacy_id}"
            self.add_triple(bdr[legacylname], rdf.type, bdo["EtextInstance"])
            self.add_triple(bda[legacylname], rdf.type, adm["AdminData"])
            self.add_triple(bda[legacylname], adm["adminAbout"], bdr[legacylname])
            self.add_triple(bda[legacylname], adm["status"], bda['StatusWithdrawn'])
            self.add_triple(bda[legacylname], adm["replaceWith"], bdr[self.lname])
        if meta.ocr_import_info is not None:
            oii = meta.ocr_import_info
            if "source" in oii:
                self.add_triple(bdr[self.lname], bdo["OPFOCRSource"], Literal(oii["source"]))
            if "software_id" in oii:
                self.add_triple(bdr[self.lname], bdo["OPFOCRSoftware"], Literal(oii["software_id"]))
                if oii["software_id"] == "norbuketaka":
                    self.add_triple(bdr[self.lname], bdo.inCollection, bdr.PR1ER1)
                    self.add_triple(bdr.PR1ER1, bdo.collectionMember, bdr[self.lname])
            if "batch_id" in oii:
                self.add_triple(bdr[self.lname], bdo["OPFOCRBatch"], Literal(oii["batch_id"]))
            if "ocr_info" in oii and "timestamp" in oii["ocr_info"]:
                self.add_triple(bdr[self.lname], bdo["OPFOCRTimeStamp"], Literal(oii["ocr_info"]["timestamp"], datatype=XSD.dateTime))
            if "timestamp" in oii:
                self.add_triple(bdr[self.lname], bdo["OPFOCRTimeStamp"], Literal(oii["timestamp"], datatype=XSD.dateTime))
        self.add_triple(
            bdr[self.lname],
            rdfs.seeAlso,
            Literal(
                f"https://github.com/Openpecha-Data/{self._pecha_id}/", datatype=XSD.anyURI
            ),
        )
        self.get_base_volumes()
        self.set_adm()

    def get_base_volumes(self):
        for baselname, baseinfo in self.openpecha.meta.bases.items():
            volume_string = self.openpecha.get_base(baselname)
            if len(volume_string) < 2:
                continue
            volume_number = 0
            if "source_metadata" in baseinfo and "volume_number" in baseinfo["source_metadata"]:
                volume_number = baseinfo["source_metadata"]["volume_number"]
            elif "order" in baseinfo:
                volume_number = baseinfo["order"]
            else:
                volume_number = int(re.search(r"\d+", baselname).group())
            iglname = None
            if "source_metadata" in baseinfo and "image_group_id" in baseinfo["source_metadata"] or "id" in baseinfo["source_metadata"]:
                iglname = baseinfo["source_metadata"]["image_group_id"] if "image_group_id" in baseinfo["source_metadata"] else baseinfo["source_metadata"]["id"]
                iglname = to_lname(iglname)
            volume_basename = f"{self.lname}_{baselname}"
            evol = bdr[f"VL{volume_basename}"]
            self.add_triple(evol, rdf.type, bdo["EtextVolume"])
            self.add_triple(evol, bdo["volumeNumber"], Literal(volume_number, datatype=XSD.integer))
            self.add_triple(evol, bdo["volumeOf"], bdr[f"{self.lname}"])
            self.add_triple(bdr[self.lname], bdo["instanceHasVolume"], evol)
            if iglname:
                self.add_triple(evol, bdo["etextVolumeForImageGroup"], bdr[iglname])
            player = self.openpecha.get_layer(baselname, LayerEnum.pagination)
            if iglname is None or self.w_info is None or player is None or self.outline_pl is None or len(self.outline_pl.get_mw_list(volume_number)) == 0:
                self.set_etext_full_volume(baselname, baseinfo, evol)
                continue
            # in outlines
            iginfo = self.w_info["image_groups"][iglname]
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
                    mws = { to_lname(self.w_info["source_metadata"]["reproduction_of"]) }
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
                self.add_partial_etext(mw, mw_i, evol, baselname, baseinfo, ranges[mw])

    def add_partial_etext(self, mw, mw_i, evol, baselname, baseinfo, rgs):
        subject = bdr[f"UT{mw}_{baselname}"]
        self.add_triple(subject, rdf.type, bdo["Etext"])
        self.add_triple(subject, bdo["eTextInInstance"], bdr[self.lname])
        self.add_triple(subject, bdo["eTextInVolume"], evol)
        self.add_triple(subject, bdo["seqNum"], Literal(mw_i, datatype=XSD.integer))
        if not rgs:
            self.add_triple(
                subject, bdo["sliceStartChar"], Literal(1, datatype=XSD.integer)
            )
        else:
            min_page_start = float('inf')
            max_page_end = 0
            min_char_start = float('inf')
            max_char_end = 0
            for rg in rgs:
                page_start, page_end, char_start, char_end = rg
                if page_start < min_page_start:
                    min_page_start = page_start
                if page_end > max_page_end:
                    max_page_end = page_end
                if char_start < min_char_start:
                    min_char_start = char_start
                if char_end > max_char_end:
                    max_char_end = char_end
            self.add_triple(
                subject, bdo["sliceStartChar"], Literal(min_char_start, datatype=XSD.integer)
            )
            self.add_triple(
                subject, bdo["sliceEndChar"], Literal(max_char_end, datatype=XSD.integer)
            )

    def set_etext_full_volume(self, baselname, baseinfo, evol):
        volume_basename = f"{self.lname}_{baselname}"
        subject = bdr[f"UT{volume_basename}"]
        self.add_triple(subject, rdf.type, bdo["Etext"])
        self.add_triple(subject, bdo["eTextInInstance"], bdr[self.lname])
        self.add_triple(subject, bdo["eTextInVolume"], evol)
        self.add_triple(subject, bdo["seqNum"], Literal(1, datatype=XSD.integer))
        # TODO?
        #self.add_triple(
        #    subject, bdo["sliceEndChar"], Literal(end, datatype=XSD.integer)
        #)
        self.add_triple(
            subject, bdo["sliceStartChar"], Literal(1, datatype=XSD.integer)
        )
        if self.include_contents:
            self.set_etext_pages(baselname)
            self.set_etext_chunks(baselname, baseinfo)

    def set_etext_pages(self, baselname):
        player = self.openpecha.get_layer(baselname, LayerEnum.pagination)
        if player is None:
            return
        for annotation_id, annotation in player.annotations.items():
            self.set_etext_page(annotation_id, annotation, baselname)

    def set_etext_page(self, annotation_id, annotation, volume_name):
        volume_basename = f"{self.lname}_{volume_name}"
        subject = bdr[f'EP{annotation_id}']
        sequence = 0
        if "imgnum" in annotation:
            sequence = annotation["imgnum"]
        elif "page_index" in annotation:
            sequence = self.get_sequence(annotation["page_index"])
        start = annotation["span"]["start"]
        end = annotation["span"]["end"]
        self.add_triple(subject, rdf.type, bdo["EtextPage"])
        self.add_triple(subject, bdo["seqNum"], Literal(sequence, datatype=XSD.integer))
        self.add_triple(
            subject, bdo["sliceEndChar"], Literal(end, datatype=XSD.integer)
        )
        self.add_triple(
            subject, bdo["sliceStartChar"], Literal(start, datatype=XSD.integer)
        )
        self.add_triple(bdr[f"UT{volume_basename}"], bdo["eTextHasPage"], subject)

    @staticmethod
    def get_sequence(page_index):
        number = int(re.search(r"\d+", page_index).group())
        return number * 2 if page_index[-1] == "b" else (number * 2) - 1


    def add_chunks(self, baselname, volume_string, language, previous_i = 0, start_cc=0, end_cc=-1):
        chunk_indexes = self.get_chunk_indexes(volume_string, language, start_cc, end_cc)
        for i in range(0, len(chunk_indexes) - 1):
            self.set_etext_chunk(
                previous_i + i, chunk_indexes[i], chunk_indexes[i + 1], baselname, volume_string, language
            )
        return previous_i + len(chunk_indexes)


    def set_etext_chunks(self, baselname, baseinfo):
        volume_string = self.openpecha.get_base(baselname)
        default_language = "bo"
        if "default_language" in baseinfo:
            default_language = baseinfo["default_language"]
        elif self.openpecha.meta.default_language is not None:
            default_language = self.openpecha.meta.default_language
        llayer = self.openpecha.get_layer(baselname, LayerEnum.language)
        if llayer is None:
            self.add_chunks(baselname, volume_string, default_language)
        else:
            last_index = 0
            ci = 0
            # for our purpose it's crucial that the annotations are returned sorted:
            sorted_annotations = sorted(llayer.annotations.values(), key=lambda x: x["span"]["start"])
            for annotation in sorted_annotations:
                if annotation["span"]["start"] > last_index:
                    ci = self.add_chunks(baselname, volume_string, default_language, ci, last_index, annotation["span"]["start"])
                ci = self.add_chunks(baselname, volume_string, annotation["language"], ci, annotation["span"]["start"], annotation["span"]["end"])
                last_index = annotation["span"]["end"]
            len_vol_str = len(volume_string)
            if last_index < len_vol_str:
                self.add_chunks(baselname, volume_string, default_language, ci, last_index, len_vol_str)

    def set_etext_chunk(self, i, start_char, end_char, baselname, volume_string, language):
        volume_basename = f"{self.lname}_{baselname}"
        etext = f"UT{volume_basename}"
        subject = bdr[f"UT{volume_basename}_{int(i):05}"]
        self.add_triple(subject, rdf.type, bdo["EtextChunk"])
        self.add_triple(
            subject,
            bdo["chunkContents"],
            Literal(volume_string[start_char:end_char], lang=language),
        )
        # TODO?
        #self.add_triple(subject, bdo["sliceEndChar"], Literal(end_char, datatype=XSD.integer))
        self.add_triple(
            subject, bdo["sliceStartChar"], Literal(1, datatype=XSD.integer)
        )

        self.add_triple(bdr[etext], bdo["eTextHasChunk"], subject)

    def set_adm(self):
        subject_r = bda[self.lname]
        einst_r = bdr[self.lname]
        graph_r = bdg[self.lname]
        if hasattr(self.openpecha, 'get_rev'):
            rev = self.openpecha.get_rev()
            self.add_triple(subject_r, adm["gitRevision"], Literal(rev))

        self.add_triple(subject_r, rdf.type, adm["AdminData"])
        self.add_triple(subject_r, adm["adminAbout"], einst_r)
        self.add_triple(subject_r, adm["graphId"], graph_r)
        self.add_triple(subject_r, adm["syncAgent"], bdr["SAOPT"])
        self.add_triple(subject_r, adm["metadataLegal"], bda["LD_BDRC_CC0"])
        

    @staticmethod
    def get_chunk_indexes(string, language, start_char = 0, end_char = 0):
        chunker = None
        if language == "bo":
            chunker = TibetanEasyChunker(string, 1500, start_char, end_char)
        else:
            chunker = EnglishEasyChunker(string, 1500, start_char, end_char)
        indexes = chunker.get_chunks()

        return indexes

    """
    Getting details of the rdf
    """

    def print_rdf(self):
        print(self.lod_g.serialize(format="ttl").decode("utf-8"))

