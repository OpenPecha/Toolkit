import os
from pathlib import Path
from urllib.parse import urljoin

import requests


class TransifexClient:
    """Transifex client to manage all the """

    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://rest.api.transifex.com"
        self.resouces_url = urljoin(self.base_url, "resources")

    def list_resouces(self, org_slug:str, project_slug:str):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        # url = urljoin(self.resouces_url, f"?filter[project]=o:{org_slug}:p:{project_slug}")
        url = "https://rest.api.transifex.com/resources/o:esukhia:p:test-2612:r:editortxt"
        response = requests.get(url, headers=headers)
        return response.json()

    def add_resouce(self, org_slug:str, project_slug:str, resouce_path: Path):
        pass

    def remove_resource(self, org_slug:str, project_slug:str, resource_slug: str):
        pass

class TransifexProject:

    def __init__(self, org_slug, project_slug):
        self.org_slug = org_slug
        self.project_slug = project_slug
        self.client = TransifexClient(token=os.getenv("TX_API_TOKEN"))

    def list_resources(self):
        return self.client.list_resouces(self.org_slug, self.project_slug)

    def remove_resource(self, resource_slug: str):
        self.client.remove_resource(self.org_slug, self.project_slug, resource_slug)




if __name__ == "__main__":
    project = TransifexProject(org_slug="esukhia", project_slug="test-2612")
    resources = project.list_resources()
    print(resources)
    project.remove_resource("texttxt")
    print(resources)
