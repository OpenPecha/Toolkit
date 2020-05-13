"""Create works in OpenPecha."""
import csv
import importlib
import importlib.util
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
import yaml
from pyewts import pyewts


class config:
    """Config class of the module."""

    resources_path = Path("resources/works")
    paths = [resources_path / "kangyur-clusters.csv"]
    instances_id_fn = resources_path / "kangyur_instances_id.txt"
    work_fn = resources_path / "W00000001.yml"
    converter = pyewts()


class Work:
    """Class for Work which contain all its the instances."""

    def __init__(self, work_fn=None):
        self.work_fn = Path(work_fn)
        self.work = self._create_or_load()

    def _create_or_load(self):
        if not self.work_fn:
            return {
                "title": None,
                "author": None,
                "bdrc-work-id": None,
                "wikidata-id": None,
                "instances": [],
            }
        return yaml.safe_load(self.work_fn.read_text())

    def save(self):
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
        except:
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


def save_work_ids(fn):
    """Extract rid work ids from given file and save.

    Args:
        fn (Path): file containing all work ids
    """
    first_col, second_col = [], []
    with fn.open() as f:
        csv_reader = csv.reader(f)
        for work_id, work_id_cat in csv_reader:
            if work_id not in first_col:
                first_col.append(work_id)
            if work_id_cat not in second_col:
                second_col.append(work_id_cat)
    work_ids = map(to_rid, first_col + second_col)
    output_fn = fn.parent / "kangyur_work_ids.txt"
    output_fn.write_text("\n".join(work_ids))
    print(f"[INFO] save at {output_fn}")


if __name__ == "__main__":
    if not config.instances_id_fn.is_file():
        for fn in config.paths:
            work_ids = save_work_ids(fn)

    work = Work(config.work_fn)
    work.add_instances(config.instances_id_fn)
    work.save()
