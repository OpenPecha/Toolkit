"""Module to support transifex integration.

Adding TM to transifex project is a premium feature.
This module provides hacky way to add TM to transifex project
by converting OpenPecha Alignment to transifex project resource
files.

Available classes:
- TransifexProject: class to represent transifex project

"""

import json
import os
import time
from pathlib import Path

import requests
from transifex.api import transifex_api

API_TOKEN = os.getenv("TX_API_TOKEN")
transifex_api.setup(auth=API_TOKEN)

class TransifexProject:
    """Class representing translation project on transifex.

    Public methods:
    - add_resource: create resource with source file.
    - add_tm: create resource with source file and it's translations,
              which act as TM.
    """

    def __init__(self, org_slug: str, project_slug: str):
        org = transifex_api.Organization.get(slug=org_slug)
        self.project = org.fetch("projects").get(slug=project_slug)
        self.resources_api_url = "https://rest.api.transifex.com/resources"

    @property
    def languages(self):
        return self.project.fetch("languages")

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
                    "slug": slug
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
            }
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

    def add_resource(self, name: str, slug: str, source_path: Path):

        print(f"[INFO] adding resource to project ({self.project.id})")

        if not source_path.is_file():
            print(f"[ERROR] FileNotFound: {source_path}")
            return

        resource_id = self._get_resource(name, slug)
        if not resource_id:
            return

        resource = self.project.fetch('resources').get(slug=slug)
        transifex_api.ResourceStringsAsyncUpload.upload(
            resource=resource,
            content=source_path.open()
        )
        print(f"[INFO] Resource created at {resource_id}")
        return resource_id

    def add_translation(self, resource_id, lang:str, content_path: Path):
        """add translation .po file to a resource"""

        url = "https://rest.api.transifex.com/resource_translations_async_uploads"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
        }
        payload = {
            "language": f"l:{lang}",
            "resource": resource_id
        }
        files = {"content": content_path.open("rb")}
        response = requests.post(url, headers=headers, data=payload, files=files)

        if response.status_code != 202:
            print("[ERROR] response:", response.json())
            return

        # check if upload has completed after every 5 secs
        upload_id = response.json()["data"]["id"]
        upload_status_check_url = f"https://rest.api.transifex.com/resource_translations_async_uploads/{upload_id}"

        while True:
            response = requests.get(upload_status_check_url, headers=headers)
            if response.status_code == 200:
                return upload_id
            time.sleep(5)

    def remove_resource(self, slug:str):
        """remvoes resource from the project"""

        resource = self.project.fetch('resources').get(slug=slug)
        resource_id = resource.id
        resource.delete()
        print(f"[INFO] Resource ({resource_id}) deleted")


    def add_tm(
        self,
        source_path: Path,
        target_path: Path,
        target_lang="en",
        resource_name="Translation Memory (don't open)",
        resource_slug="tm"
    ):
        """add .po format translation memory to the project"""

        print(f"[INFO] adding TM to project ({self.project.id})")

        resource_id = self.add_resource(name=resource_name, slug=resource_slug, source_path=source_path)
        if not resource_id:
            print(f"[ERROR] failed to add translation memory to project {self.project.id}")
            return
        upload_id = self.add_translation(
            resource_id=resource_id,
            lang=target_lang,
            content_path=target_path
        )
        if not upload_id:
            print("[ERROR] failed to upload translation")
            self.remove_resource(slug=resource_slug)

        print(f"[INFO] Successfully added TM to project ({self.project.id})")



if __name__ == "__main__":
    project = TransifexProject("esukhia", "test-2612")
    # project.remove_resource(slug="tm")
    # project.remove_resource(slug="translatethis")
    print("[INFO] Adding source file")
    project.add_resource(
        name="Translate this",
        slug="translatethis",
        source_path=Path("./tests/data/alignment/test-bo.po"),
    )
    project.add_tm(
        source_path=Path("./tests/data/alignment/test-bo.po"),
        target_path=Path("./tests/data/alignment/test-en.po")
    )
