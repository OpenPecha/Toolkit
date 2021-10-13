"""
This module contains all the functions required for Transifex integeration
"""

import json
import os
from pathlib import Path

import requests
from transifex.api import transifex_api

API_TOKEN = os.getenv("TX_API_TOKEN")
transifex_api.setup(auth=API_TOKEN)

class TransifexProject:
    """Class represents translation project on transifex"""

    def __init__(self, org_slug: str, project_slug: str):
        org = transifex_api.Organization.get(slug=org_slug)
        self.project = org.fetch("projects").get(slug=project_slug)
        self.resources_api_url = "https://rest.api.transifex.com/resources"

    @property
    def languages(self):
        return self.project.fetch("languages")


    def add_translation(self, resource_slug: str):
        language = transifex_api.Language.get(code="en")
        resource = self.project.fetch('resources').get(slug=resource_slug)
        translations = transifex_api.ResourceTranslation.\
            filter(resource=resource, language=language).\
            include('resource_string')
        return translations

    def _create_empty_resource(self, name, slug):
        """creates empty resource if doesn't exists yet and return resource id"""

        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-type": "application/vnd.api+json"
        }
        payload = {
            "data": {
                "attributes": {
                    "accept_translations": True,
                    "categories": [
                        "category_1",
                        "category_2"
                    ],
                    "name": name,
                    "priority": "normal",
                    "slug": slu)g
                },
                "relationships": {
                    "i18n_format": {
                        "data": {
                            "id": "PO",
                            "type": "i18n_formats"
                        }
                    },
                    "project": {
                        "data": {
                            "id": self.project.id,
                            "type": "projects"
                        }
                    }
                },
                "type": "resources"
            })
        }

        response = requests.post(self.resources_api_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()["data"]["id"]

    def _get_resource_id(self, slug:str):
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
        }
        url =  f"{self.resources_api_url}/{self.project.id}:r:{slug}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()["data"]["id"]

    def _get_resource(self, name:str, slug:str):
        resource_id = self._create_empty_resource(name, slug)
        if not resource_id:
            resource_id = self._get_resource_id(slug)
        if not resource_id:
            print("[ERROR] couldn't create the resouce or get existing resource")
            return
        return resource_id

    def add_resource(self, name: str, slug: str, content_path: Path):
        if not content_path.is_file():
            print(f"[ERROR] FileNotFound: {content_path}")
            return

        resource_id = self._get_resource(name, slug)
        if not resource_id:
            return

        resource = self.project.fetch('resources').get(slug=slug)
        transifex_api.ResourceStringsAsyncUpload.upload(
            resource=resource,
            content=content_path.open()
        )
        print(f"[INFO] Resource created at {resource_id}")



if __name__ == "__main__":
    project = TransifexProject("esukhia", "test-2612")
    project.add_resource("test-tm", "testtm", Path("./tests/data/alignment/test.po"))
