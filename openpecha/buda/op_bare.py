from openpecha.buda.op import Openpecha
from git import Repo
from pathlib import Path
from openpecha.buda.layer import Layer
from openpecha.buda.chunker import *


class OpenpechaBare(Openpecha):
    """
    A class inheriting from the Openpecha class that defines the path to the local bare git repo.

    TODO: conceptually there's really a lot in common with op_fs.py as it's just reading an OPF folder
          in a git repo, but the implementation is completely different because the way to access files
          in a bare git repo is very specific. This could also be considered a serializer, like op_fs.py.
    """
    def __init__(self, lname, path_to_bare_git):
        Openpecha.__init__(self, lname)
        self.path = Repo(str(Path(path_to_bare_git, self.lname)))

    def get_meta(self):
        """
        Getting the meta data from the file in .opf
        """
        repo = self.path
        meta_content = repo.git.show(f'{self.commit}:{self.lname}.opf/meta.yml')

        meta_dic = self.read_yaml(meta_content)

        self.meta = meta_dic

    def get_files(self):
        """
        Getting all the files in the bare repo
        """
        files = self.path.git.ls_tree(r='HEAD').split("\n")

        files = [file.split("\t")[-1] for file in files]

        return files

    def get_last_commit(self):
        repo = self.path
        return repo.git.rev_parse('HEAD')

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
                        dic[path[1]].append(path[-1])
                    else:
                        dic[path[1]][path[-2]].append(path[-1])
                except KeyError:
                    if path[-2] == 'base':
                        dic[path[1]] = []
                        dic[path[1]].append(path[-1])
                    else:
                        self.sort_layers(dic, path[-3:])

        return dic

    def get_base(self):
        """
        Getting the base of the .opf file from the local repo, it is located in lname.opf/base/version/
        """
        files = self.split_files()

        for file in files['base']:
            self.base_layer[file] = self.path.git.show(f'{self.commit}:{self.lname}.opf/base/{file}')

    def get_layer(self, volume, file):
        """
        Create a Layer object with the following params:
        - Openpecha ref
        - layer file name
        - path to bare repo
        """
        layer = Layer(self.lname, file, volume, self.path, True)

        return layer
