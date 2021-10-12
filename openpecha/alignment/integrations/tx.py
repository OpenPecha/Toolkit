"""
This module contains all the functions required for Transifex integeration
"""

import os
from pathlib import Path
from urllib.parse import urljoin

import requests
from transifex.api import transifex_api

API_TOKEN = os.getenv("TX_API_TOKEN")
transifex_api.setup(auth=API_TOKEN)

class TransifexProject:
    """Class represents translation project on transifex"""

    def __init__(self, org_slug: str, project_slug: str):
        self.org_slug = org_slug
        self.project_slug = project_slug
        org = transifex_api.Organization.get(slug=self.org_slug)
        self.project = org.fetch("projects").get(slug=self.project_slug)

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
        url = urljoin(
            "https://rest.api.transifex.com/resources",
            f"?filter[project]=o:{self.org_slug}:p:{self.project_slug}"
        )
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-type": "application/vnd.api+json"
        }
        payload = {
            "data": {
                "attributes": {
                    "accept_translations": True,
                    "name": name,
                    "slug": slug,
                },
            }
        }

        response = requests.post(url, headers=headers, data=payload)
        print(response.json())


    def add_resource(self, name: str, slug: str, content_path: Path):
        pass



if __name__ == "__main__":
    project = TransifexProject("esukhia", "test-2612")
    project.add_resource("test-tm", "testtm", Path("./tests/data/alignment/test.po"))
