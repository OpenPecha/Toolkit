from urllib import request, parse
import sys
import json

class Error:
    def __init__(self, type, content):
        self.type = type
        self.content = content
        self.print_error()

    def print_error(self):
        print(self.content, file=sys.stderr)
