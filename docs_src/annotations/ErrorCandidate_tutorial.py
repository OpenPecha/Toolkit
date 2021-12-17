from openpecha.core.annotations import ErrorCandidate, Span

error_candidate = ErrorCandidate(span=Span(start=10, end=30))

assert error_candidate.span.start == 10
