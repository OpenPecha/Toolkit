from docs_src.annotations.Archaic_tutorial import archaic
from docs_src.annotations.Citation_tutorial import citation
from docs_src.annotations.Correction_tutorial import correction
from docs_src.annotations.Durchen_tutorial import durchen
from docs_src.annotations.ErrorCandidate_tutorial import error_candidate
from docs_src.annotations.Footnote_tutorial import footnote
from docs_src.annotations.Pagination_tutorial import pagination
from docs_src.annotations.Pedurma_tutorial import pedurma
from docs_src.annotations.Sabche_tutorial import sabche
from docs_src.annotations.Segment_tutorial import segment
from docs_src.annotations.Tsawa_tutorial import tsawa
from docs_src.annotations.Yigchung_tutorial import yigchung


def test_ppagination():
    assert pagination.span.start == 10


def test_citation():
    assert citation.span.start == 10


def test_correction():
    assert correction.span.start == 10


def test_error_candidate():
    assert error_candidate.span.start == 10


def test_pedurma():
    assert pedurma.span.start == 10


def test_sabche():
    assert sabche.span.start == 10


def test_tsawa():
    assert tsawa.span.start == 10


def test_yighcung():
    assert yigchung.span.start == 10


def test_archaic():
    assert archaic.span.start == 10


def test_durchen():
    assert durchen.span.start == 10


def test_footnote():
    assert footnote.span.start == 10


def test_segment():
    assert segment.span.start == 10
