import json
import sys
from urllib import parse, request


class Error:
    def __init__(self, type, content):
        self.type = type
        self.content = content
        self.print_error()

    def print_error(self):
        print(self.content, file=sys.stderr)
