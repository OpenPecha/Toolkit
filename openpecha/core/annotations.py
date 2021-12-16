"""Module contains all the Annotations classes
"""

from typing import Dict, Optional

from pydantic import BaseModel, Extra, Field, validator


class Span(BaseModel):
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)

    @validator("*")
    def span_must_not_be_neg(cls, v):
        if v < 0:
            raise ValueError("span shouldn't be negative")
        return v

    @validator("end")
    def end_must_not_be_less_than_start(cls, v, values, **kwargs):
        if "start" in values and v < values["start"]:
            raise ValueError("Span end must not be less than start")
        return v

    class Config:
        extra = Extra.forbid


class BaseAnnotation(BaseModel):
    span: Span
    metadata: Dict = {}

    class Config:
        extra = Extra.forbid


class Pagination(BaseAnnotation):
    page_info: str = Field(None, description="page payload")
    imgnum: int = Field(None, description="image sequence number")
    order: int = Field(None, description="order of the page")
    reference: str = Field(
        None, description="can be url or just string indentifier of source page"
    )


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
    pass


class Footnote(BaseAnnotation):
    pass


class Segment(BaseAnnotation):
    pass
