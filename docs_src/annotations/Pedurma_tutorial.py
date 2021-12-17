from openpecha.core.annotations import Pedurma, Span

pedurma = Pedurma(span=Span(start=10, end=30))

assert pedurma.span.start == 10
