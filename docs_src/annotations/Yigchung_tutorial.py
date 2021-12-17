from openpecha.core.annotations import Span, Yigchung

yigchung = Yigchung(span=Span(start=10, end=30))

assert yigchung.span.start == 10
