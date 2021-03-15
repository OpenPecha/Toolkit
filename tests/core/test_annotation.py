import pytest
from pydantic import ValidationError

from openpecha.core.annotation import Span


def test_span_end_must_not_be_less_than_start():
    with pytest.raises(ValidationError):
        Span(start=2, end=1)
