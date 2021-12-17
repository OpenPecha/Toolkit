from openpecha.core.annotations import Archaic, Span

archaic = Archaic(span=Span(start=10, end=30))

assert archaic.span.start == 10
