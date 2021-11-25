"""OpenPecha Work

This module contains OpenPecha Work data model and utils for
creating work objects.
"""
from typing import Dict, List, Optional

from pydantic import BaseModel, validator

from .ids import get_work_id


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
