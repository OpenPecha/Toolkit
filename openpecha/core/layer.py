from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, validator

from .utils import get_unique_id


class LayerEnum(Enum):
    book_title = "BookTitle"
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


class InitialCreationEnum(Enum):
    ocr = "ocr"
    ebook = "ebook"
    input = "input"


class Layer(BaseModel):
    id: str = None
    annotation_type: LayerEnum
    revision: str
    annotations: Dict

    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        return v or get_unique_id()

    @validator("revision")
    def revision_must_int_parsible(cls, v):
        assert v.isdigit(), "must integer parsible like `00002`"
        return v


class MetaData(BaseModel):
    id: str
    initial_creation_type: InitialCreationEnum
    source_metadata: Optional[Dict] = {}
