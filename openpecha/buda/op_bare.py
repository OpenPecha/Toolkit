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
    def __init__(self, lname, path=None, repo=None, rev="HEAD"):
        Openpecha.__init__(self, lname)
        self.rev = rev
        if repo is not None:
            self.repo = repo
        else:
            self.repo = Repo(path)

    def read_file_content(self, oppath):
        return repo.git.show(f'{self.rev}:{self.lname}.opf/'+oppath)

    def read_file_content_yml(self, oppath):
        ymlstr = repo.git.show(f'{self.rev}:{self.lname}.opf/'+oppath)
        return yaml.safe_load(file)

    def list_files(self):
        """
        Getting all the files in the bare repo
        """
        files = self.repo.git.ls_tree(r=self.rev).split("\n")
        files = [file.split("\t")[-1] for file in files]

        return files
