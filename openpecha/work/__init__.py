"""OpenPecha Work

This module contains OpenPecha Work data model and utils for
creating work objects.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

from pydantic import BaseModel, validator
from pydantic.networks import AnyHttpUrl

from .. import config
from ..core.ids import get_work_id
from ..core.metadata import InitialCreationType
from ..utils import download_pecha, dump_yaml, load_yaml


class InstanceMetadata(BaseModel):
    """OpenPecha Work instance metadata."""

    source_id: str
    initial_creation_type: InitialCreationType
    title: str
    author: str = None
    organization: AnyHttpUrl
    created_at: datetime
    last_modified_at: datetime


class Instance(BaseModel):
    """Instance model

    This model represents a single instance of a work.
    """

    id: str
    metadata: InstanceMetadata


class WorkNotFound(Exception):
    """Work not found exception."""

    pass


class Work(BaseModel):
    """OpenPecha Work

    This class contains OpenPecha Work data model.
    """

    id: str = None
    bdrc_id: str = None
    title: str
    alternative_titles: List[str] = []
    author: str = None
    isRoot: bool = None
    language: str = None
    type_defination: str = None
    wikidata_id: str = None
    instances: Dict[str, Dict] = {}

    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        return v or get_work_id()

    def add_instance(self, instance: Instance):
        """Add instance to work.

        Args:
            instance (Dict): Instance to add to work.
        """
        self.instances[instance.id] = instance.metadata.dict()

    def get_instance(self, instance_id: str) -> Instance:
        """Get instance from work.

        Args:
            instance_id (str): Instance id to get from work.

        Returns:
            instance: Instance from work.
        """
        metadata = self.instances.get(instance_id)
        if not metadata:
            return None
        return Instance(id=instance_id, metadata=InstanceMetadata(**metadata))

    def remove_instance(self, instance_id: str):
        """Remove instance from work.

        Args:
            instance_id (str): Instance id to remove from work.
        """
        del self.instances[instance_id]

    @classmethod
    def from_yaml(cls, fn: Union[str, Path]) -> "Work":
        """Create Work from yaml file.

        Args:
            fn (str): YAML file name.

        Returns:
            Work: Work object.
        """
        fn = Path(fn)
        data = load_yaml(fn)
        work = cls.parse_obj(data)
        for instance_id, metadata in work.instances.items():
            work.instances[instance_id] = InstanceMetadata.parse_obj(metadata)
        return work

    def save_to_yaml(self, output_dir: Union[str, Path] = None) -> Path:
        """Save work to yaml file.

        Args:
            output_dir (str): Output directory.

        Returns:
            Path: Path to saved yaml file.
        """
        if not output_dir:
            output_dir = download_pecha(config.WORKS_REPO_NAME)
        output_dir = Path(output_dir)
        work_fn = output_dir / f"{self.id}.yaml"
        dump_yaml(data=json.loads(self.json()), output_fn=work_fn)
        return work_fn

    @classmethod
    def from_id(cls, id_: str) -> "Work":
        """Create Work from id.

        Args:
            id (str): Work id.

        Returns:
            Work: Work object.
        """
        works_path = download_pecha(config.WORKS_REPO_NAME)
        work_fn = works_path / f"{id_}.yaml"
        if not work_fn.is_file():
            work_fn = works_path / f"{id_}.yml"
            if not work_fn.is_file():
                raise WorkNotFound(f"Work {id_} not found")
        return cls.from_yaml(work_fn)
