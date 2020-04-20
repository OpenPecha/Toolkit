import yaml
from tqdm import tqdm
from git import Repo
from pathlib import Path

from openpecha.buda.layer import Layer


class Openpecha:
    """
    The Openpecha class that correspond to the https://github.com/OpenPecha/openpecha-catalog catalog.
    """
    def __init__(self, lname, path, commit='master'):
        """
        Initializing the openpecha object with it's name from https://github.com/OpenPecha/openpecha-catalog
        The path is the path to the local repo
        Commit is the commit we want, by default the last commit on master
        """
        self.lname = lname
        self.bare_repo_path = Repo(str(Path(path, self.lname)))
        self.commit = commit
        self.meta = self.get_meta()
        self.base_layer = {}
        self.layers = {}

    def get_meta(self):
        """
        Getting the meta data from the file in .opf
        """
        repo = self.bare_repo_path
        meta_dic = yaml.safe_load(repo.git.show(f'{self.commit}:{self.lname}.opf/meta.yml'))

        return meta_dic

    def get_base(self):
        """
        Getting the base of the .opf file from the local repo, it is located in lname.opf/base/version/
        """
        files = self.split_files()

        for file in files['base']:
            self.base_layer[file] = self.bare_repo_path.git.show(f'{self.commit}:{self.lname}.opf/base/{file}')

    def get_layers(self):
        """
        Getting all the layers and storing them in a Layer object, the layers are located in lname.opf/layers/volume/
        """
        files_dic = self.split_files()

        for volume in files_dic['layers']:
            self.layers[volume] = {}
            for file in tqdm(files_dic['layers'][volume], ascii=True, desc=f'{self.lname} {volume}'):
                self.layers[volume][file] = self.get_layer(volume, file)

    def get_layer(self, volume, file):
        """
        Create a Layer object with the following params:
        - Openpecha ref
        - layer file name
        - path to bare repo
        """
        layer = Layer(self.lname, file, volume, self.bare_repo_path)

        return layer

    def get_files(self):
        """
        Getting all the files in the bare repo
        """
        files = self.bare_repo_path.git.ls_tree(r='HEAD').split("\n")

        files = [file.split("\t")[-1] for file in files]

        return files

    @staticmethod
    def sort_layers(dic, path):
        """
        Sorting the layers by their volume number
        """
        if path[1] in dic:
            dic[path[1]][path[-2]] = []
        else:
            dic[path[1]] = {}
            dic[path[1]][path[-2]] = []
        dic[path[1]][path[-2]].append(path[-1])

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
                        self.sort_layers(dic, path)

        return dic

