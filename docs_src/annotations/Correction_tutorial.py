from openpecha.core.annotations import Correction, Span

correction = Correction(span=Span(start=10, end=30))

assert correction.span.start == 10
