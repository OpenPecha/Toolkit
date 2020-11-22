from openpecha.config import N_SIG, PECHA_PREFIX


def create_pecha_id(num):
    return f"{PECHA_PREFIX}{num:0{N_SIG}}"
