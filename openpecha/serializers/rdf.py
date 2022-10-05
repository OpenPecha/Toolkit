import re
from pathlib import Path
import rdflib
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD, Namespace, NamespaceManager
from openpecha.buda.chunker import TibetanEasyChunker, EnglishEasyChunker
from openpecha.core.layer import Layer, LayerEnum, PechaMetadata, SpanINFO

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

class BUDARDFSerializer:
    """
    """

    def __init__(self, openpecha):
        self.openpecha = openpecha
        self._pecha_id = openpecha.meta.id
        self.lname = f"IE0OP{self._pecha_id}"
        self.graph_r = bdg[self.lname]
        self.lod_ds = rdflib.Dataset()
        self.lod_g = self.lod_ds.graph(self.graph_r)
        self.lod_g.namespace_manager = nsm
        self.bl_volinfo = None

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
            scanlname = sm["id"]
            if scanlname.startswith("bdr:"):
                scanlname = scanlname[4:]
            elif scanlname.startswith("http://purl.bdrc.io/resource/"):
                scanlname = scanlname[29:]
            self.add_triple(
                bdr[self.lname], bdo["instanceReproductionOf"], bdr[scanlname]
            )
            self.add_triple(
                bdr[scanlname], bdo["instanceHasReproduction"], bdr[self.lname]
            )
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
            if "batch_id" in oii:
                self.add_triple(bdr[self.lname], bdo["OPFOCRBatch"], Literal(oii["batch_id"]))
            if "ocr_info" in oii and "timestamp" in oii["ocr_info"]:
                self.add_triple(bdr[self.lname], bdo["OPFOCRTimeStamp"], Literal(oii["ocr_info"]["timestamp"], datatype=XSD.dateTime))
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
            self.set_etext_asset(baselname, baseinfo, volume_number)
            self.add_triple(
                bdr[self.lname],
                bdo["instanceHasVolume"],
                bdr[f"VL{self.lname}_{baselname}"],
            )
            self.set_etext_ref(baselname)
            self.set_etext(baselname, baseinfo, volume_number)

    def set_etext_asset(self, baselname, baseinfo, volume_number):
        volume_basename = f"{self.lname}_{baselname}"
        subject = bdr[f"VL{volume_basename}"]
        self.add_triple(subject, rdf.type, bdo["VolumeEtextAsset"])
        self.add_triple(subject, bdo["volumeHasEtext"], bdr[f"ER{volume_basename}"])
        self.add_triple(
            subject, bdo["volumeNumber"], Literal(volume_number, datatype=XSD.integer)
        )
        self.add_triple(subject, bdo["volumeOf"], bdr[f"{self.lname}"])

    def set_etext_ref(self, baselname):
        volume_basename = f"{self.lname}_{baselname}"
        subject = bdr[f"ER{volume_basename}"]
        self.add_triple(subject, rdf.type, bdo["EtextRef"])
        self.add_triple(subject, bdo["eTextResource"], bdr[f"UT{volume_basename}"])
        self.add_triple(subject, bdo["seqNum"], Literal(1, datatype=XSD.integer))

    def set_etext(self, baselname, baseinfo, volume_number):
        volume_basename = f"{self.lname}_{baselname}"
        subject = bdr[f"UT{volume_basename}"]
        if "source_metadata" in baseinfo and "image_group_id" in baseinfo["source_metadata"]:
            iglname = baseinfo["source_metadata"]["image_group_id"]
            if iglname.startswith("bdr:"):
                iglname = iglname[4:]
            elif iglname.startswith("http://purl.bdrc.io/resource/"):
                iglname = iglname[29:]
            self.add_triple(subject, bdo["eTextForImageGroup"], bdr[iglname])
        self.add_triple(subject, rdf.type, bdo["Etext"])
        self.add_triple(subject, bdo["eTextInInstance"], bdr[self.lname])
        self.add_triple(
            subject, bdo["eTextIsVolume"], Literal(volume_number, datatype=XSD.integer)
        )
        self.add_triple(
            subject,
            rdfs.seeAlso,
            Literal(
                f"https://github.com/Openpecha-Data/{self._pecha_id}/", datatype=XSD.anyURI
            ),
        )
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
        self.add_triple(
            subject, bdo["sliceEndChar"], Literal(end_char, datatype=XSD.integer)
        )
        self.add_triple(
            subject, bdo["sliceStartChar"], Literal(start_char, datatype=XSD.integer)
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

