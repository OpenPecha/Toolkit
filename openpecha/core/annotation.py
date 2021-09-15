from typing import Dict, Optional

from pydantic import BaseModel, validator


class Span(BaseModel):
    start: int
    end: int

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


class AnnBase(BaseModel):
    span: Span
    metadata: Dict = {}


class Page(AnnBase):
    page_info: Optional[str] = None  # page payload
    imgnum: Optional[
        int
    ] = None  # image sequence no. from bdrc api, http://iiifpres.bdrc.io/il/v:bdr:I0888
    reference: Optional[str] = None  # image filename from bdrc
