from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Extra, validator

from . import ids


class InitialCreationType(Enum):
    ocr = "ocr"
    ebook = "ebook"
    input = "input"


class CopyrightStatus(Enum):
    UNKNOWN = "Unknown"
    COPYRIGHTED = "In copyright"
    PUBLIC_DOMAIN = "Public domain"


class Copyright(BaseModel):
    status: CopyrightStatus = CopyrightStatus.UNKNOWN
    notice: Optional[str] = ""
    info_url: Optional[str] = None

    class Config:
        extra = Extra.forbid

Copyright_copyrighted = Copyright(
    status=CopyrightStatus.COPYRIGHTED,
    notice="In copyright by the original author or editor",
    info_url="http://rightsstatements.org/vocab/InC/1.0/",
)

Copyright_unknown = Copyright(
    status=CopyrightStatus.UNKNOWN,
    notice="Copyright Undertermined",
    info_url="http://rightsstatements.org/vocab/UND/1.0/",
)

Copyright_public_domain = Copyright(
    status=CopyrightStatus.PUBLIC_DOMAIN,
    notice="Public domain",
    info_url="https://creativecommons.org/publicdomain/mark/1.0/",
)

class LicenseType(Enum):
    # based on https://creativecommons.org/licenses/

    CC0 = "CC0"
    PUBLIC_DOMAIN_MARK = "Public Domain Mark"
    CC_BY = "CC BY"
    CC_BY_SA = "CC BY-SA"
    CC_BY_ND = "CC BY-ND"
    CC_BY_NC = "CC BY-NC"
    CC_BY_NC_SA = "CC BY-NC-SA"
    CC_BY_NC_ND = "CC BY-NC-ND"
    
    UNDER_COPYRIGHT = "under copyright"


class PechaMetadata(BaseModel):
    id: str = None
    legacy_id: Optional[str] = None
    ocr_import_info: Optional[Dict] = None
    default_language: str = None
    source: str = None
    source_file: str = None
    initial_creation_type: InitialCreationType
    imported: datetime = None
    last_modified: datetime = None
    parser: AnyHttpUrl = None
    source_metadata: Optional[Dict] = None  # place to dump any metadata from the source
    statistics: Optional[Dict] = None
    quality: Optional[Dict] = None
    bases: Optional[Dict[str, Dict]] = {}
    copyright: Copyright = None
    license: LicenseType = None

    @validator("imported", pre=True, always=True)
    def set_imported_date(cls, v):
        return v or datetime.now()

    @validator("last_modified", pre=True, always=True)
    def set_last_modified_date(cls, v):
        return v or datetime.now()

    @validator("copyright", pre=True, always=True)
    def set_copyright_info(cls, v):
        return v or Copyright()

    def update_last_modified_date(self):
        self.last_modified = datetime.now()

    # class Config:
    #     extra = Extra.forbid


class InitialPechaMetadata(PechaMetadata):
    bases: Dict = {}

    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        return v or ids.get_initial_pecha_id()


class OpenPechaMetadata(PechaMetadata):
    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        return v or ids.get_open_pecha_id()


class DiplomaticPechaMetadata(PechaMetadata):
    @validator("id", pre=True, always=True)
    def set_id(cls, v):
        return v or ids.get_diplomatic_id()
