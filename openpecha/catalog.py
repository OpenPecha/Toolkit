import requests
from openpecha.github_utils import update_catalog_data


class Catalog:

    def __init__(self):
        self.repo_name = "openpecha-catalog"
        self.batch_path = "data/batch.csv"
        self.last_id_path = "data/last_id"


    @property
    def last_id(self):
        last_id_url = 'https://raw.githubusercontent.com/OpenPecha/openpecha-catalog/master/data/last_id'
        r = requests.get(last_id_url)
        return int(r.content.decode('utf-8').strip()[1:])

    def _add_id_url(self, row):
        id = row[0]
        row[0] = f'[{id}](https://github.com/OpenPecha/{id})'
        return row

    def create_batch_catalog(self, batch):
        # update last_id
        content = batch[-1][0]
        update_catalog_data(self.repo_name, self.last_id_path, content, "update last id of Pecha", update=True)

        # create batch.csv
        content = '\n'.join([','.join(row) for row in map(self._add_id_url, batch)])
        update_catalog_data(self.repo_name, self.batch_path, content, "create new batch")
        print('[INFO] Updated the OpenPecha catalog')



if __name__ == "__main__":
    catalog = Catalog()
    last_id = catalog.last_id
    batch = [
        [f'P{last_id+1:06}', 'title', 'vol', 'author', 'src id'],
        [f'P{last_id+2:06}', 'title1', 'vol1', 'author1', 'src id1']
    ]
    catalog.create_batch_catalog(batch)
