import random
from uuid import uuid4


def get_uuid():
    return uuid4().hex


def get_id(prefix, length):
    return prefix + "".join(random.choices(uuid4().hex, k=length)).upper()
