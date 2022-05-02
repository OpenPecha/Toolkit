from openpecha.core.annotations import Durchen, Span

base = "སེམས་ཅན་རྣམས་ལ་སླུ་བ་ཡི།"
durchen = Durchen(
    span=Span(start=15, end=18),
    default="སྡེ།",
    options={"ཅོ།": "སླུ་", "པེ།": "བསླུ།", "སྣར།": "བསླུ།"},
)

assert base[durchen.span.start : durchen.span.end + 1] == "སླུ་"
