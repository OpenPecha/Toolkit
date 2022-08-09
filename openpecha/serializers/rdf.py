import re
from pathlib import Path
import rdflib
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD, Namespace, NamespaceManager
from openpecha.buda.tibetan_easy_chunker import TibetanEasyChunker
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

    def get_bl_volinfo(self):
        if self.bl_volinfo is not None:
            return self.bl_volinfo
        bases = self.openpecha.meta.bases
        for base, binfo in bases.items():

        if meta is None or "source_metadata" not in meta or "volumes" not in meta["source_metadata"]:
            self.bl_volinfo = {}
            return {}
        volumes = meta["source_metadata"]["volumes"]
        res = {}
        for vol in volumes.values():
            if "base_file" in vol:
                res[vol["base_file"]] = vol
        self.bl_volinfo = res
        return res

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
            elif scanuri.startswith("http://purl.bdrc.io/resource/"):
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
                    bdr[self.lname], bdo["OPFOCRWordMedianConfidenceIndex"], Literal(meta.statistics["ocr_word_median_confidence_index"], datatyle=XSD.float)
                )
            if "ocr_word_mean_confidence_index" in meta.statistics:
                self.add_triple(
                    bdr[self.lname], bdo["OPFOCRWordMeanConfidenceIndex"], Literal(meta.statistics["ocr_word_mean_confidence_index"], datatyle=XSD.float)
                )
        if meta.legacy_id is not None and meta.legacy_id:
            legacylname = f"IE0OP{self.legacy_id}"
            self.add_triple(bdr[legacylname], rdf.type, bdo["EtextInstance"])
            self.add_triple(bda[legacylname], rdf.type, adm["AdminData"])
            self.add_triple(bda[legacylname], adm["adminAbout"], bdr[legacylname])
            self.add_triple(bda[legacylname], adm["status"], bda['StatusWithdrawn'])
            self.add_triple(bda[legacylname], adm["replaceWith"], bdr[self.lname])
        if meta.ocr_import_info is not None:
            oii = meta.ocr_import_info
            if "source" in oii:
                self.add_triple(bdr[legacylname], bdo["OPFOCRSource"], Literal(oii["source"]))
            if "software" in oii:
                self.add_triple(bdr[legacylname], bdo["OPFOCRSoftware"], Literal(oii["software"]))
            if "batch" in oii:
                self.add_triple(bdr[legacylname], bdo["OPFOCRBatch"], Literal(oii["batch"]))
            if "ocr_info" in oii and "timestamp" in oii["ocr_info"]:
                self.add_triple(bdr[legacylname], bdo["OPFOCRTimeStamp"], Literal(oii["ocr_info"]["timestamp"], XSD.dateTime))
        self.get_base_volumes()
        self.set_adm()

    def get_base_volumes(self):
        for baselname, baseinfo in self.openpecha.meta.bases:
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
        volume_number = int(re.search(r"\d+", baselname).group())
        if "source_metadata" in baseinfo and "image_group_id" in baseinfo["source_metadata"]:
            iglname = baseinfo["source_metadata"]
            if iglname.startswith("bdr:"):
                iglname = iglname[4:]
            elif iglname.startswith("http://purl.bdrc.io/resource/")
                iglname = iglname[29:]
            self.add_triple(subject, bdo["eTextForImageGroup"], bdr[iglname])
        subject = bdr[f"UT{volume_basename}"]
        self.add_triple(subject, rdf.type, bdo["Etext"])
        self.add_triple(subject, bdo["eTextInInstance"], bdr[self.lname])
        self.add_triple(
            subject, bdo["eTextIsVolume"], Literal(volume_number, datatype=XSD.integer)
        )
        self.add_triple(
            subject,
            rdfs.seeAlso,
            Literal(
                f"https://github.com/OpenPecha/{self._pecha_id}/", datatype=XSD.anyURI
            ),
        )
        self.set_etext_pages(baselname)
        self.set_etext_chunks(baselname)

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

    def set_etext_chunks(self, volume_name):
        volume_string = self.openpecha.get_base(volume_name)
        chunk_indexes = self.get_chunk_index(volume_string)

        for i in range(0, len(chunk_indexes) - 2):
            self.set_etext_chunk(
                i, chunk_indexes[i], chunk_indexes[i + 1], volume_name, volume_string
            )

    def set_etext_chunk(self, i, start_char, end_char, volume_name, volume_string):
        volume_basename = f"{self.lname}_{volume_name}"
        etext = f"UT{volume_basename}"
        subject = bdr[f"UT{volume_basename}_{int(i):05}"]

        self.add_triple(subject, rdf.type, bdo["EtextChunk"])
        self.add_triple(
            subject,
            bdo["chunkContents"],
            Literal(volume_string[start_char:end_char], lang="bo"),
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
        rev = self.openpecha.get_rev()

        self.add_triple(subject_r, rdf.type, adm["AdminData"])
        self.add_triple(subject_r, adm["adminAbout"], einst_r)
        self.add_triple(subject_r, adm["graphId"], graph_r)
        self.add_triple(subject_r, adm["syncAgent"], bdr["SAOPT"])
        self.add_triple(subject_r, adm["metadataLegal"], bda["LD_BDRC_CC0"])
        self.add_triple(subject_r, adm["gitRevision"], Literal(rev))

    @staticmethod
    def get_chunk_index(string):
        chunker = TibetanEasyChunker(string, 1500)
        indexes = chunker.get_chunks()

        return indexes

    """
    Getting details of the rdf
    """

    def print_rdf(self):
        print(self.lod_g.serialize(format="ttl").decode("utf-8"))

