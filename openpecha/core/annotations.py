"""Module contains all the Annotations classes
"""

from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .ids import get_uuid


class Span(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)
    errors: Optional[Dict] = None

    @field_validator("start", "end")
    @classmethod
    def span_must_not_be_neg(cls, v):
        if v < 0:
            raise ValueError("span shouldn't be negative")
        return v

    @model_validator(mode='after')
    def end_must_not_be_less_than_start(self):
        if self.start is not None and self.end < self.start:
            raise ValueError("Span end must not be less than start")
        return self


class BaseAnnotation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    span: Span
    metadata: Optional[Dict] = None


class Pagination(BaseAnnotation):
    page_info: str = Field(None, description="page payload")
    imgnum: int = Field(None, description="image sequence number")
    order: int = Field(None, description="order of the page")
    reference: str = Field(
        None, description="can be url or just string indentifier of source page"
    )


class Language(BaseAnnotation):
    language: str = Field(None, description="BCP-47 tag of the language")


class OCRConfidence(BaseAnnotation):
    confidence: float
    nb_below_threshold: Optional[int]


class TranscriptionTimeSpan(BaseAnnotation):
    time_span: Span


class Citation(BaseAnnotation):
    pass


class Correction(BaseAnnotation):
    pass


class ErrorCandidate(BaseAnnotation):
    pass


class Pedurma(BaseAnnotation):
    pass


class Sabche(BaseAnnotation):
    pass


class Tsawa(BaseAnnotation):
    pass


class Yigchung(BaseAnnotation):
    pass


class Archaic(BaseAnnotation):
    pass


class Durchen(BaseAnnotation):
    default: str = Field(..., description="text_name of the default option")
    options: Dict[str, str] = Field(
        ..., description="all other spell options in dict of {text_name, option}"
    )
    printable: bool = True


class Footnote(BaseAnnotation):
    pass


class Segment(BaseAnnotation):
    pass
