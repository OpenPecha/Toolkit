from openpecha.core.annotations import Pagination, Span

pagination = Pagination(span=Span(start=10, end=30))

assert pagination.span.start == 10
