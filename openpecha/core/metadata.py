from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Extra, validator

from .ids import get_pecha_id


class InitialCreationType(Enum):
    ocr = "ocr"
    ebook = "ebook"
    input = "input"


class PechaMetadata(BaseModel):
    id: str = None
    source: str = None
    source_file: str = None
    initial_creation_type: InitialCreationType
    imported: datetime = None
    last_modified: datetime = None
    parser: AnyHttpUrl = None
    source_metadata: Optional[Dict] = {}  # place to dump any metadata from source
    statistics: Dict[str, Union[int, float, str]] = {}
    quality: Dict[str, Union[int, float]] = {}

    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        return v or get_pecha_id()

    @validator("imported", pre=True, always=True)
    def set_imported_date(cls, v):
        return v or datetime.now()

    @validator("last_modified", pre=True, always=True)
    def set_last_modified_date(cls, v):
        return v or datetime.now()

    def update_last_modified_date(self):
        self.last_modified = datetime.now()

    class Config:
        extra = Extra.forbid
