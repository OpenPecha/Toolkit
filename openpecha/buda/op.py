import pathlib

import yaml


class Openpecha:
    """
    The Openpecha class that correspond to the https://github.com/OpenPecha/openpecha-catalog catalog.

    TODO: for this class and its implementations, function signatures should be changed a bit:
       - get_layer_list(basefname): lists all the layers in the directory corresponding to basename (and cache it)
       - get_layer(basefname, layerfname): get the content of the layer, put it in the object if not presen
       - get_base_list(): get an array of all the layers fnames (and cache it)
       - get_base(basefname): get the string of base layer (and cache it)
    """

    def __init__(self, lname):
        """
        Initializing the openpecha object with it's name from https://github.com/OpenPecha/openpecha-catalog
        Commit is the commit we want, by default the last commit on master
        """
        self.lname = lname
        self.meta = None
        self.bases = {}
        self.layers = {}
        self.components = self.read_components()

    def read_layer(self, basename, layername):
        return self.read_file_content_yml(
            "layers/" + basename + "/" + layername + ".yml"
        )

    def read_base(self, basename):
        return self.read_file_content("base/" + basename + ".txt")

    def read_meta(self):
        """
        Getting the meta.yml
        """
        return self.read_file_content_yml("meta.yml")

    def get_meta(self):
        if self.meta is not None:
            return self.meta
        self.meta = self.read_meta()
        return self.meta

    def is_ocr(self):
        meta = self.get_meta()
        if "source_metadata" in meta:
            sour = meta["source_metadata"]["id"].split(":")
            if sour[0] == "bdr":
                return True
        return False

    def get_base(self, basename):
        if basename in self.bases:
            return self.bases[basename]
        if basename not in self.components["base"]:
            return None
        self.bases[basename] = self.read_base(basename)
        return self.bases[basename]

    def get_layer(self, basename, layername):
        if basename in self.layers and layername in self.layers[basename]:
            return self.layers[basename][layername]
        if basename not in self.components["base"] or basename not in self.components["layers"]:
            return None
        if layername not in self.components["layers"][basename]:
            return None
        if basename not in self.layers:
            self.layers[basename] = {}
        self.layers[basename][layername] = self.read_layer(basename, layername)
        return self.layers[basename]

    def has_layer(self, basename, layername):
        return layername in self.components["layers"][basename]

    def list_layers(self, basename):
        if basename not in self.components["layers"]:
            return None
        return self.components["layers"][basename]

    def list_base(self):
        return self.components["base"]

    def read_components(self):
        """
        get all bases and layers
        """
        paths = self.list_paths()
        res = {"base": [], "layers": {}}

        for f in sorted(paths):
            path = f.split("/")
            if len(path) > 1:
                if path[-2] == "base":
                    basename = pathlib.Path(path[-1]).stem
                    res["base"].append(basename)
                else:
                    basename = path[-2]
                    layername = pathlib.Path(path[-1]).stem
                    if basename not in res["layers"]:
                        res["layers"][basename] = []
                    res["layers"][basename].append(layername)
        return res
