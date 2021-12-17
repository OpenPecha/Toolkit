from openpecha.core.annotations import Footnote, Span

footnote = Footnote(span=Span(start=10, end=30))

assert footnote.span.start == 10
