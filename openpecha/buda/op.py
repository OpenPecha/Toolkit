import yaml
from tqdm import tqdm


class Openpecha:
    """
    The Openpecha class that correspond to the https://github.com/OpenPecha/openpecha-catalog catalog.
    """
    def __init__(self, lname, commit='master'):
        """
        Initializing the openpecha object with it's name from https://github.com/OpenPecha/openpecha-catalog
        Commit is the commit we want, by default the last commit on master
        """
        self.lname = lname
        self.commit = commit
        self.meta = {}
        self.base_layer = {}
        self.layers = {}

    @staticmethod
    def read_yaml(yaml_content):
        return yaml.safe_load(yaml_content)

    def get_layers(self):
        """
        Getting all the layers and storing them in a Layer object, the layers are located in lname.opf/layers/volume/
        """
        files_dic = self.split_files()

        for volume in files_dic['layers']:
            self.layers[volume] = {}
            for file in tqdm(files_dic['layers'][volume], ascii=True, desc=f'{self.lname} {volume}'):
                self.layers[volume][file] = self.get_layer(volume, file)

    @staticmethod
    def sort_layers(dic, path):
        """
        Sorting the layers by their volume number
        """
        if path[0] in dic:
            dic[path[0]][path[1]] = []
        else:
            dic[path[0]] = {}
            dic[path[0]][path[1]] = []
        dic[path[0]][path[1]].append(path[2])


