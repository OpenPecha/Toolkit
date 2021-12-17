from openpecha.core.annotations import Durchen, Span

durchen = Durchen(span=Span(start=10, end=30))

assert durchen.span.start == 10
