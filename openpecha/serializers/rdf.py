import re
from pathlib import Path

from openpecha.buda.op_bare import OpenpechaBare
from openpecha.buda.op_fs import OpenpechaFS
from openpecha.buda.tibetan_easy_chunker import TibetanEasyChunker
from openpecha.serializers.rdf_setup import *


class Rdf:
    """
    TODO:
    - rename in BUDARDFSerializer
    - initialize with an OpenPecha instead of a path
    """

    def __init__(self, oplname, openpecha):
        self.oplname = oplname
        self.lname = f"IE0OP{self.oplname}"
        self.graph_r = bdg[self.lname]
        self.lod_ds = rdflib.Dataset()
        self.lod_g = self.lod_ds.graph(self.graph_r)
        self.lod_g.namespace_manager = nsm
        self.openpecha = openpecha

    def add_triple(self, rdf_subject, rdf_predicate, rdf_object):
        self.lod_g.add((rdf_subject, rdf_predicate, rdf_object))

    def get_graph(self):
        self.set_instance()
        return self.lod_g

    """
    Entry point to build the RDF graph
    """

    def set_instance(self):
        self.add_triple(bdr[f"{self.lname}"], rdf.type, bdo["EtextInstance"])
        meta = self.openpecha.get_meta()
        if "source_metadata" in meta:
            sour = meta["source_metadata"]["id"].split(":")
            if sour[0] == "bdr":
                self.add_triple(
                    bdr[self.lname], bdo["instanceReproductionOf"], bdr["M" + sour[-1]]
                )
                self.add_triple(
                    bdr["M" + sour[-1]], bdo["instanceHasReproduction"], bdr[self.lname]
                )
                self.add_triple(
                    bdr[self.lname], bdo["instanceReproductionOf"], bdr[sour[-1]]
                )
                self.add_triple(
                    bdr[sour[-1]], bdo["instanceHasReproduction"], bdr[self.lname]
                )
        self.get_base_volumes()
        self.set_adm()

    def get_base_volumes(self):
        for volume_name in self.openpecha.list_base():
            self.set_etext_asset(volume_name)
            self.add_triple(
                bdr[self.lname],
                bdo["instanceHasVolume"],
                bdr[f"VL{self.lname}_{volume_name}"],
            )
            self.set_etext_ref(volume_name)
            self.set_etext(volume_name)

    def set_etext_asset(self, volume_name):
        volume_basename = f"{self.lname}_{volume_name}"
        volume_number = int(re.search(r"\d+", volume_name).group())
        subject = bdr[f"VL{volume_basename}"]

        self.add_triple(subject, rdf.type, bdo["VolumeEtextAsset"])
        self.add_triple(subject, bdo["volumeHasEtext"], bdr[f"ER{volume_basename}"])
        self.add_triple(
            subject, bdo["volumeNumber"], Literal(volume_number, datatype=XSD.integer)
        )
        self.add_triple(subject, bdo["volumeOf"], bdr[f"{self.lname}"])

    def set_etext_ref(self, volume_name):
        volume_basename = f"{self.lname}_{volume_name}"
        subject = bdr[f"ER{volume_basename}"]

        self.add_triple(subject, rdf.type, bdo["EtextRef"])
        self.add_triple(subject, bdo["eTextResource"], bdr[f"UT{volume_basename}"])
        self.add_triple(subject, bdo["seqNum"], Literal(1, datatype=XSD.integer))

    def set_etext(self, volume_name):
        volume_basename = f"{self.lname}_{volume_name}"
        volume_number = int(re.search(r"\d+", volume_name).group())
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
                f"https://github.com/OpenPecha/{self.oplname}/", datatype=XSD.anyURI
            ),
        )
        self.set_etext_pages(volume_name)
        self.set_etext_chunks(volume_name)

    def set_etext_pages(self, volume_name):
        player = self.openpecha.get_layer(volume_name, "pagination")
        if player is None:
            return
        if "pagination" in player:
            player = player["pagination"]
        if "annotations" not in player:
            return
        for annotation in player["annotations"]:
            self.set_etext_page(annotation, volume_name)

    def set_etext_page(self, annotation, volume_name):
        volume_basename = f"{self.lname}_{volume_name}"
        subject = bdr[f'EP{annotation["id"]}']
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
        self.add_triple(subject_r, adm["status"], bda["StatusReleased"])
        self.add_triple(subject_r, adm["access"], bda["AccessOpen"])

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

    def rdf(self):
        return self.lod_g
