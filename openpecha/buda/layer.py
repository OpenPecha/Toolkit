import yaml


class Layer:
    """
    The Layer object initiated with:
    - The Openpecha lname it belongs to
    - The filename of the current layer
    - The volume it is a layer of
    - The path to the bare repo
    """
    def __init__(self, op_lname, layer_file, volume, bare_repo_path):
        self.op_lname = op_lname
        self.layer_file = layer_file
        self.volume = volume
        self.bare_repo_path = bare_repo_path
        self.annotations = self.get_annotations()
        self.annotation_type = self.get_type()
        self.revision = self.get_revision()
        self.id = self.get_id()

    def get_type(self):
        """
        Get the type of annotation from the YAML file
        """
        return self.read_file()['annotation_type']

    def get_revision(self):
        """
        Get the revision number from the YAML file
        """
        return self.read_file()['revision']

    def get_id(self):
        """
        Get the id of the layer file from the YAML file
        """
        return self.read_file()['id']

    def get_annotations(self):
        """
        Get all the annotations from the YAML file
        """
        return self.read_file()['annotations']

    def read_file(self):
        """
        Read all the content of the file stored in the local bare repo
        """
        file = self.bare_repo_path.git.show(f'master:{self.op_lname}.opf/layers/{self.volume}/{self.layer_file}')
        meta_dic = yaml.safe_load(file)

        return meta_dic
