"""Create works in OpenPecha."""
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

import requests
import yaml
from pyewts import pyewts


class config:
    """Config class of the module."""

    resources_path = Path("resources/works")
    bdrc_outlines_path = resources_path / "db" / "tbrc" / "tbrc-outlines"
    work_fn = resources_path / "W00000001.yml"
    work_output = Path("../works/")
    converter = pyewts()


class Work:
    """Class for Work which contain all its the instances."""

    def __init__(self, work_fn=None):
        self.work_fn = Path(work_fn) if work_fn else work_fn
        self.work = self._create_or_load()

    def __repr__(self):
        return f"Work(title={self.work['title']}, author={self.work['author']}, bdrc-work-id={self.work['bdrc-work-id']}, n_instances={len(self.work['instances'])})"

    def _create_or_load(self):
        if not self.work_fn:
            return {
                "title": "",
                "author": "",
                "bdrc-work-id": "",
                "wikidata-id": "",
                "instances": [],
            }
        return yaml.safe_load(self.work_fn.read_text())

    def save(self, fn):
        self.work_fn = fn
        yaml.dump(
            self.work,
            self.work_fn.open("w"),
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        print(f"[INFO] work is save at: {self.work_fn}")

    def _to_rid(self, work_id):
        """Return rid version of work_id."""
        return work_id[0] + work_id[2:]

    def _get_title(self, rid):
        """Return title for instances with `rid`."""
        bdrc_metadata_url = f"https://www.tbrc.org/xmldoc?rid={rid}"
        r = requests.get(bdrc_metadata_url)
        try:
            root = ET.fromstring(r.content.decode("utf-8"))
        except Exception:
            return ""
        title_tag = root[0]
        return config.converter.toUnicode(title_tag.text)

    def _get_instances_id(self, fn):
        for work_id in fn.read_text().split("\n"):
            yield work_id.strip()

    def create_instance(self, title, rid, g_ocr=None, n_ocr=None, trans=None):
        instance = {title: {}}
        for k, v in [
            ("bdrc-instance-id", rid),
            ("google-ocr", g_ocr),
            ("namsel-ocr", n_ocr),
            ("transcription", trans),
        ]:
            if not v:
                continue
            instance[title][k] = v
        return instance

    def add_instances(self, instances_id_fn):
        for inst_id in self._get_instances_id(instances_id_fn):
            print(f"\t- adding isntance {inst_id}")
            title = self._get_title(inst_id)
            instance = self.create_instance(title, inst_id)
            self.work["instances"].append(instance)


def clean_text_id(text_id):
    if not text_id:
        return ""
    cats = "  abcd"
    text_id = text_id.strip()
    if text_id == "00":
        return ""
    elif "-" in text_id:
        id_, cat = text_id.split("-")
        if not cat or len(cat) > 1:
            return ""
        return f"{id_}{cats[int(cat.strip())]}"
    elif ";" in text_id:
        return text_id.split(";")[0].strip()
    else:
        return f"D{text_id}"


def get_value(parent, child, attr, convert=False):
    for node in parent.getElementsByTagName(f"outline:{child}"):
        attrs = node.attributes
        if "type" in attrs and attrs["type"].value == attr:
            childnodes = node.childNodes
            if not childnodes:
                return ""
            value = childnodes[0].data
            if convert:
                return config.converter.toUnicode(value)
            return value
    return ""


def get_works_from_bdrc_outlines(fn):
    dom = minidom.parse(str(fn))
    for node in dom.getElementsByTagName("outline:node"):
        if node.attributes["type"].value != "text":
            continue
        bdrc_work_id = node.attributes["RID"].value
        title = get_value(node, "title", "bibliographicalTitle", convert=True)
        author = get_value(node, "creator", "hasMainAuthor", convert=True)
        # toh = get_value(node, "description", "toh")
        # bdrc_work_id = clean_text_id(toh)
        if title or author or bdrc_work_id:
            work = Work()
            work.work["title"] = title
            work.work["author"] = author
            work.work["bdrc-work-id"] = bdrc_work_id
            yield work


if __name__ == "__main__":
    for i, work in enumerate(
        get_works_from_bdrc_outlines(config.bdrc_outlines_path / "O2MS16391.xml"),
        start=4,
    ):
        work_fn = config.work_output / f"W{i:08}.yml"
        print(work)
        work.save(work_fn)
