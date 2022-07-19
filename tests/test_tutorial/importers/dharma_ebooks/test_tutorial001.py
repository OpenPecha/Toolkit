import os
import shutil
from docs_src.importers.dharma_ebooks.tutorial001 import opf_path
from openpecha.utils import remove_dir



def test_dharama_ebooks_parser():
    remove_dir(opf_path.parent)

