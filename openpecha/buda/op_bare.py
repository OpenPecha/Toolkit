from pathlib import Path

import yaml
from git import Repo

from openpecha.buda.op import Openpecha


class OpenpechaBare(Openpecha):
    """
    A class inheriting from the Openpecha class that defines the path to the local bare git repo.

    TODO: conceptually there's really a lot in common with op_fs.py as it's just reading an OPF folder
          in a git repo, but the implementation is completely different because the way to access files
          in a bare git repo is very specific. This could also be considered a serializer, like op_fs.py.
    """

    def __init__(self, lname, path=None, repo=None, rev="HEAD"):
        self.rev = rev
        if repo is not None:
            self.repo = repo
        else:
            self.repo = Repo(path)
        Openpecha.__init__(self, lname)

    def get_rev(self):
        return self.rev

    def read_file_content(self, oppath):
        return self.repo.git.show(f"{self.rev}:{self.lname}.opf/" + oppath)

    def read_file_content_yml(self, oppath):
        ymlstr = self.repo.git.show(f"{self.rev}:{self.lname}.opf/" + oppath)
        return yaml.safe_load(ymlstr)

    def list_paths(self):
        """
        Getting all the files in the bare repo
        """
        files = self.repo.git.ls_tree(r=self.rev).split("\n")
        # removing the xxx.opf at the beginning
        files = [file.split("\t")[-1] for file in files]
        files = [
            file[len(self.lname) + 5 :]
            for file in files
            if file.startswith(self.lname + ".")
            and (file.endswith(".txt") or file.endswith(".yml"))
        ]
        return files
