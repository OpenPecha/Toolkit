from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, validator

from .utils import get_id, get_uuid


class LayerEnum(Enum):
    index = "index"

    book_title = "BookTitle"
    sub_title = "SubTitle"
    book_number = "BookNumber"
    poti_title = "PotiTitle"
    author = "Author"
    chapter = "Chapter"

    topic = "Text"
    sub_topic = "SubText"

    pagination = "Pagination"
    citation = "Citation"
    correction = "Correction"
    error_candidate = "ErrorCandidate"
    peydurma = "Peydurma"
    sabche = "Sabche"
    tsawa = "Tsawa"
    yigchung = "Yigchung"
    archaic = "Archaic"
    durchen = "Durchen"
    footnote = "Footnote"
    segment = "Segment"


class InitialCreationEnum(Enum):
    ocr = "ocr"
    ebook = "ebook"
    input = "input"


class Layer(BaseModel):
    id: str = None
    annotation_type: LayerEnum
    revision: str = "00001"
    annotations: Dict = {}

    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        return v or get_uuid()

    @validator("revision")
    def revision_must_int_parsible(cls, v):
        assert v.isdigit(), "must integer parsible like `00002`"
        return v

    def bump_revision(self):
        self.revision = f"{int(self.revision)+1:05}"

    def reset(self):
        self.revision = "00001"
        self.annotations = {}


class PechaMetaData(BaseModel):
    id: str = None
    initial_creation_type: InitialCreationEnum
    source_metadata: Optional[Dict] = {}
    created_at: datetime = None
    last_modified_at: datetime = None

    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        return v or get_id(prefix="P", length=8)
