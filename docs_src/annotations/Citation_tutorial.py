from openpecha.core.annotations import Citation, Span

citation = Citation(span=Span(start=10, end=30))

assert citation.span.start == 10
