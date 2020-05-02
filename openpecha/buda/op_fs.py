from openpecha.buda.op import Openpecha
from openpecha.buda.layer import Layer
from openpecha.buda.chunker import *
from os import walk


class OpenpechaFS(Openpecha):
    """
    A class inheriting from the Openpecha class that defines the path to the local .opf folder

    TODO: perhaps this should be renamed OPF and be moved into serializers/ as it's really a reader/serializer for an .opf folder

    TODO: we could also implement write functions. Basically there would be:
       - readFromPath(path): would more or less replace the current __init__
       - writeToPath(path): would write the content to a path (removing all files that used to be there)
    """
    def __init__(self, lname, path_to_opf):
        Openpecha.__init__(self, lname)
        self.path = path_to_opf

    def get_meta(self):
        """
        Getting the meta data from the file in .opf
        """
        opf = self.path
        f = open(f'{opf}/meta.yml', "r")

        meta_dic = self.read_yaml(f.read())

        self.meta = meta_dic

    def get_files(self):
        """
        Getting all the files in the bare repo
        """
        files = []

        for (dirpath, dirnames, filenames) in walk(self.path):
            for file in filenames:
                files.append(f'{dirpath}/{file}'.replace(self.path, ""))


        return files

    def split_files(self):
        """
        Sorting the files in .opf as either base or layers
        """
        files = self.get_files()
        dic = {}

        for f in files:
            path = f.split("/")

            if len(path) > 2:
                try:
                    if path[-2] == 'base':
                        dic['base'].append(path[-1])
                    else:
                        dic['layers'][path[-2]].append(path[-1])
                except KeyError:
                    if path[-2] == 'base':
                        dic['base'] = []
                        dic['base'].append(path[-1])
                    else:
                        self.sort_layers(dic, path[-3:])

        return dic

    def get_base(self):
        """
        Getting the base of the .opf file from the local repo, it is located in lname.opf/base/version/
        """
        files = self.split_files()
        opf = self.path

        for file in files['base']:
            f = open(f'{opf}/base/{file}', "r")

            self.base_layer[file] = f.read()

    def get_layer(self, volume, file):
        """
        Create a Layer object with the following params:
        - Openpecha ref
        - layer file name
        - path to .opf
        """
        layer = Layer(self.lname, file, volume, self.path, False)

        return layer
