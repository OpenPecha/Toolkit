'''catalog module contains all the functionalities necessary for managin
the catalog. Functonalities includes:
    - Creating opfs from input text
    - Assiging ID to the new opf
    - Updating the catalog with new opfs

'''

import requests
from openpecha.github_utils import create_file
from openpecha.github_utils import github_publish
from openpecha.utils import *


buildin_pipes = {
    'input': {
        'ocr_result_input': ocr_result_input
    },
    'release': {
        'create_release_with_assets': create_release_with_assets
    }
}


class CatalogManager:
    '''Manages the catalog'''

    def __init__(self, pipes=None, FormatterClass=None, not_include_files=['resources']):
        self.repo_name = "openpecha-catalog"
        self.batch_path = "data/batch.csv"
        self.last_id_path = "data/last_id"
        self.batch = []
        self.current_id = last_id()
        self.FormatteClass = FormatterClass
        self.not_include_files = not_include_files
        self.pipes = pipes if pipes else buildin_pipes


    def last_id(self):
        '''returns the id assigin to last opf pecha'''
        last_id_url = 'https://raw.githubusercontent.com/OpenPecha/openpecha-catalog/master/data/last_id'
        r = requests.get(last_id_url)
        return int(r.content.decode('utf-8').strip()[1:])

    
    def _add_id_url(self, row):
        id = row[0]
        row[0] = f'[{id}](https://github.com/OpenPecha/{id})'
        return row


    def update_catalog(self):
        '''Updates the catalog csv to have new opf-pechas metadata'''
        # update last_id
        content = batch[-1][0]
        create_file(self.repo_name, self.last_id_path, content, "update last id of Pecha", update=True)

        # create batch.csv
        content = '\n'.join([','.join(row) for row in map(self._add_id_url, batch)])
        create_file(self.repo_name, self.batch_path, content, "create new batch")
        print('[INFO] Updated the OpenPecha catalog')

    
    def format_and_publish(path):
        '''Convert input pecha to opf-pecha with id assigined'''
        formatter = self.FormatteClass()
        pecha_path = formatter.create_opf(path)
        github_publish(pecha_path, not_includes=self.not_include_files)
        return pecha_path





if __name__ == "__main__":
    catalog = Catalog()
    last_id = catalog.last_id
    batch = [
        [f'P{last_id+1:06}', 'title', 'vol', 'author', 'src id'],
        [f'P{last_id+2:06}', 'title1', 'vol1', 'author1', 'src id1']
    ]
    catalog.create_batch_catalog(batch)
