from openpecha.core.pecha import OpenPechaFS

pecha = OpenPechaFS(path="<path_to_pecha>")

pecha.update_base("v001", "new content")
pecha.save()
