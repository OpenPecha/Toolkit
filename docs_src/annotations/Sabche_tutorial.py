from openpecha.core.annotations import Sabche, Span

sabche = Sabche(span=Span(start=10, end=30))

assert sabche.span.start == 10
