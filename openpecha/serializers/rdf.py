import re
from pathlib import Path
from openpecha.serializers.rdf_setup import *
from openpecha.buda.op_fs import OpenpechaFS
from openpecha.buda.op_bare import OpenpechaBare
from openpecha.buda.tibetan_easy_chunker import TibetanEasyChunker


class Rdf:
    """
    TODO: 
    - rename in RDFSerializer
    - initialize with an OpenPecha instead of a path
    """
    def __init__(self, lname, path=str(Path.home()/'.openpecha/data'), from_git=True):
        self.graphname = lname
        self.lod_ds = rdflib.Dataset()
        self.lod_g = self.lod_ds.graph(bdg[self.graphname])
        self.lod_g.namespace_manager = nsm
        self.openpecha = self.create_openpecha(lname, path, from_git)
        self.setup_openpecha()

    def graph(self):
        return self.lod_g

    def add_triplet(self, rdf_subject, rdf_predicate, rdf_object):
        self.lod_g.add((rdf_subject, rdf_predicate, rdf_object))

    @staticmethod
    def create_openpecha(lname, path, git):
        if git:
            return OpenpechaBare(lname, path)
        else:
            return OpenpechaFS(lname, path)

    """
    Setting up the openpecha, getting all the base_layers and extra layers
    """
    def setup_openpecha(self):
        self.get_op_base_layers()
        self.get_op_layers()
        self.get_op_meta()

    def get_op_base_layers(self):
        self.openpecha.get_base()

    def get_op_layers(self):
        self.openpecha.get_layers()

    def get_op_meta(self):
        self.openpecha.get_meta()

    """
    Building the RDF graph
    """
    def set_instance(self):
        self.add_triplet(bdr[f'IE0{self.graphname}'], rdf.type, bdo["EtextInstance"])
        if self.openpecha.meta.get('source_metadata'):
            self.parse_meta()
        self.get_base_volumes()
        self.set_adm()


    def parse_meta(self):
        sour = self.openpecha.meta['source_metadata']['id'].split(":")
        self.add_triplet(bdr[f'IE0{self.graphname}'], bdo['instanceReproductionOf'], globals()[sour[0]][sour[-1]])

    def get_base_volumes(self):
        for volume in self.openpecha.base_layer.items():
            self.set_etext_asset(volume)
            self.add_triplet(bdr[f'IE0{self.graphname}'], bdo['instanceHasVolume'],
                             bdr[f'VLIE0{self.graphname}_{volume[0].replace(".txt", "")}'])
            self.set_etext_ref(volume)
            self.set_etext(volume)

    def set_etext_asset(self, volume):
        volume_name = f'IE0{self.graphname}_{volume[0].replace(".txt", "")}'
        volume_number = int(re.search(r'\d+', volume[0].replace(".txt", "")).group())
        subject = bdr[f'VL{volume_name}']

        self.add_triplet(subject, rdf.type, bdo['VolumeEtextAsset'])
        self.add_triplet(subject, bdo['volumeHasEtext'], bdr[f'ER{volume_name}'])
        self.add_triplet(subject, bdo['volumeNumber'], Literal(volume_number, datatype=XSD.integer))
        self.add_triplet(subject, bdo['volumeOf'], bdr[f'IE0{self.graphname}'])

    def set_etext_ref(self, volume):
        volume_name = f'IE0{self.graphname}_{volume[0].replace(".txt", "")}'
        subject = bdr[f'ER{volume_name}']

        self.add_triplet(subject, rdf.type, bdo['EtextRef'])
        self.add_triplet(subject, bdo['eTextResource'], bdr[f'UT{volume_name}'])
        self.add_triplet(subject, bdo['seqNum'], Literal(1, datatype=XSD.integer))

    def set_etext(self, volume):
        volume_name = f'IE0{self.graphname}_{volume[0].replace(".txt", "")}'
        volume_number = int(re.search(r'\d+', volume[0].replace(".txt", "")).group())
        subject = bdr[f'UT{volume_name}']

        self.add_triplet(subject, rdf.type, bdo['Etext'])
        self.add_triplet(subject, bdo['eTextInInstance'], bdr[volume_name])
        self.add_triplet(subject, bdo['eTextIsVolume'], Literal(volume_number, datatype=XSD.integer))
        self.add_triplet(subject, rdfs.seeAlso, Literal(f'https://github.com/OpenPecha/{self.graphname}/', datatype=XSD.anyURI))
        self.set_etext_pages(volume)
        self.set_etext_chunks(volume)

    def set_etext_pages(self, volume):
        volume_number = volume[0].replace(".txt", "")
        annotations = self.openpecha.layers[volume_number]['pagination.yml'].annotations

        for annotation in annotations:
            self.set_etext_page(annotation, volume)

    def set_etext_page(self, annotation, volume):
        volume_name = f'IE0{self.graphname}_{volume[0].replace(".txt", "")}'
        subject = bdr[f'EP{annotation["id"]}']
        sequence = self.get_sequence(annotation['page_index'])
        start = annotation['span']['start']
        end = annotation['span']['end']

        self.add_triplet(subject, rdf.type, bdo['EtextPage'])
        self.add_triplet(subject, bdo['seqNum'], Literal(sequence, datatype=XSD.integer))
        self.add_triplet(subject, bdo['sliceEndChar'], Literal(end, datatype=XSD.integer))
        self.add_triplet(subject, bdo['sliceStartChar'], Literal(start, datatype=XSD.integer))

        self.add_triplet(bdr[f'UT{volume_name}'], bdo['eTextHasPage'], subject)

    @staticmethod
    def get_sequence(page_index):
        number = int(re.search(r'\d+', page_index).group())
        return number * 2 if page_index[-1] == 'b' else (number * 2) - 1

    def set_etext_chunks(self, volume):
        volume_string = self.openpecha.base_layer[volume[0]]
        chunk_indexes = self.get_chunk_index(volume_string)

        for i in range(0, len(chunk_indexes) - 2):
            self.set_etext_chunk(i, chunk_indexes[i], chunk_indexes[i + 1], volume)

    def set_etext_chunk(self, i, start_char, end_char, volume):
        volume_name = f'IE0{self.graphname}_{volume[0].replace(".txt", "")}'
        volume_string = self.openpecha.base_layer[volume[0]]
        etext = f'UT{volume_name}'
        subject = bdr[f'UT{volume_name}_{int(i):05}']

        self.add_triplet(subject, rdf.type, bdo['EtextChunk'])
        self.add_triplet(subject, bdo['chunkContents'], Literal(volume_string[start_char:end_char], lang="bo"))
        self.add_triplet(subject, bdo['sliceEndChar'], Literal(end_char, datatype=XSD.integer))
        self.add_triplet(subject, bdo['sliceStartChar'], Literal(start_char, datatype=XSD.integer))

        self.add_triplet(bdr[etext], bdo['eTextHasChunk'], subject)

    def set_adm(self):
        subject = bda[f'IE0{self.graphname}']
        commit = self.openpecha.get_last_commit()

        self.add_triplet(subject, rdf.type, adm['AdminData'])
        self.add_triplet(subject, adm['adminAbout'], subject)
        self.add_triplet(subject, adm['metadataLegal'], bda['LD_BDRC_CC0'])
        self.add_triplet(subject, adm['openPechaCommit'], Literal(commit))
        self.add_triplet(subject, adm['status'], bda['StatusReleased'])

    @staticmethod
    def get_chunk_index(string):
        chunker = TibetanEasyChunker(string, 1500)
        indexes = chunker.get_chunks()

        return indexes

    """
    Getting details of the rdf
    """
    def print_rdf(self):
        print(self.lod_g.serialize(format='ttl').decode("utf-8"))

    def rdf(self):
        return self.lod_g


