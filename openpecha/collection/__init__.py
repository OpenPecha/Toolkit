import yaml
import os
import shutil
from pathlib import Path
from openpecha import config
from openpecha.cli import download_pecha
from openpecha.serializers import HFMLSerializer

class Collections:
  
    def __init__(self, output_path=config.COLLECTIONS_PATH):
        self.file_names = []
        self.output_path = output_path
        self.curr_collection = {}
        self.collections = {}
           
    def get_all(self):
        pecha_path = download_pecha("collections", self.output_path)
        collections_path = Path(f"{pecha_path}/collections") 
        for file in os.listdir(collections_path):
            if file.endswith(".yml"):
                yml_content = Path(f"{collections_path}/{file}").read_text(encoding='utf-8')
                content = yaml.safe_load(yml_content)
                self.curr_collection[file[:-4]]={
                    'id': content['id'],
                    'title': content['title'],
                    'works': content['works'],
                    'instances': content['instances']
                }
                self.collections.update(self.curr_collection)
        return self.collections
  
  
class Collection:

    def __init__(self, name, output_path=config.COLLECTIONS_PATH):
        self.name = name
        self.pecha_ids = []
        self.output_path = output_path

    def bundle_items(self, items=[]):
        for item in items:
            pecha_path = download_pecha(item, self.output_path)
            self.pecha_ids.append(pecha_path.name)
        return self.pecha_ids
  
    def export(self, format=None):
        for dir in os.listdir(f"{self.output_path}"):
            if dir != "collections":
                self.pecha_ids.append(dir)
                

        if format == "plain":
            export_path = Path(f"{self.output_path}/{self.name}")
            export_path.mkdir(exist_ok=True, parents=True)
            for pecha_id in self.pecha_ids:
                meta_yml = Path(f"{self.output_path}/{pecha_id}/{pecha_id}.opf/meta.yml").read_text(encoding='utf-8')
                content = yaml.safe_load(meta_yml)
                if pecha_id[0] == "P":
                    title = content['source_metadata']['title'][:20]
                elif pecha_id[0] == "W":
                    title = content['title'][:20]
                for file in os.listdir(f"{self.output_path}/{pecha_id}/{pecha_id}.opf/base"):
                    if file.endswith(".txt"):
                        base_content = Path(f"{self.output_path}/{pecha_id}/{pecha_id}.opf/base/{file}").read_text(encoding='utf-8')
                        Path(f"{export_path}/{title}_{file}").write_text(base_content, encoding='utf-8')

        shutil.make_archive(export_path, "zip", export_path)
        return export_path._str 
