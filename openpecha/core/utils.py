from uuid import uuid4


def get_unique_id():
    return uuid4().hex
