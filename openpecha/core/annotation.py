"""
TODO: will be replaced by ./annotations.py
"""

from typing import Dict, Optional

from pydantic import BaseModel, field_validator, model_validator


class Span(BaseModel):
    start: int
    end: int

    @field_validator("start", "end")
    @classmethod
    def span_must_not_be_neg(cls, v):
        if v < 0:
            raise ValueError("span shouldn't be negative")
        return v

    @model_validator(mode='after')
    def end_must_not_be_less_than_start(self):
        if self.end < self.start:
            raise ValueError("Span end must not be less than start")
        return self


class AnnBase(BaseModel):
    span: Span
    metadata: Optional[Dict] = None


class Page(AnnBase):
    page_info: Optional[str] = None  # page payload
    imgnum: Optional[
        int
    ] = None  # image sequence no. from bdrc api, http://iiifpres.bdrc.io/il/v:bdr:I0888
    reference: Optional[str] = None  # image filename from bdrc
