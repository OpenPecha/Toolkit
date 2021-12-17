from openpecha.core.annotations import Span, Tsawa

tsawa = Tsawa(span=Span(start=10, end=30))

assert tsawa.span.start == 10
