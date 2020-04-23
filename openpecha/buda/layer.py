import yaml


class Layer:
    """
    The Layer object initiated with:
    - The Openpecha lname it belongs to
    - The filename of the current layer
    - The volume it is a layer of
    - The path to the bare repo
    """
    def __init__(self, op_lname, layer_file, volume, path, is_git):
        self.op_lname = op_lname
        self.layer_file = layer_file
        self.volume = volume
        self.path = path
        self.is_git = is_git
        raw = self.get_raw()
        self.annotations = self.get_annotations(raw)
        self.annotation_type = self.get_type(raw)
        self.revision = self.get_revision(raw)
        self.id = self.get_id(raw)

    @staticmethod
    def get_type(raw):
        """
        Get the type of annotation from the YAML file
        """
        return raw['annotation_type']

    @staticmethod
    def get_revision(raw):
        """
        Get the revision number from the YAML file
        """
        return raw['revision']

    @staticmethod
    def get_id(raw):
        """
        Get the id of the layer file from the YAML file
        """
        return raw['id']

    @staticmethod
    def get_annotations(raw):
        """
        Get all the annotations from the YAML file
        """
        return raw['annotations']

    def get_raw(self):
        if self.is_git:
            return self.read_git()
        else:
            return self.read_file()

    def read_git(self):
        """
        Read all the content of the file stored in the local bare repo
        """
        file = self.path.git.show(f'master:{self.op_lname}.opf/layers/{self.volume}/{self.layer_file}')
        meta_dic = yaml.safe_load(file)

        return meta_dic

    def read_file(self):
        """
        Read all the content of the file stored in the local .opf
        """
        f = open(f'{self.path}/layers/{self.volume}/{self.layer_file}', "r")

        meta_dic = yaml.safe_load(f.read())

        return meta_dic
