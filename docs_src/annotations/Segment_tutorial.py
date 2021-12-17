from openpecha.core.annotations import Segment, Span

segment = Segment(span=Span(start=10, end=30))

assert segment.span.start == 10
