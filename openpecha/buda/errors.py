from urllib import request, parse
import sys
import json
from openpecha import config


class Error:
    def __init__(self, type, content):
        self.type = type
        self.content = content
        self.spread_the_word()

    def send_to_slack(self):
        """
        This function posts to a private slack channel, make sure you have your webhook url in a file called config.py,
        in the following format:
        WEBHOOK_URL = 'your_webhook_url'
        """
        post = {"text": "{0}".format(self.content)}

        try:
            json_data = json.dumps(post)
            url = getattr(config, "WEBHOOK_URL", "No URL found for your webhook")
            req = request.Request(url,
                                  data=json_data.encode('ascii'),
                                  headers={'Content-Type': 'application/json'})
            resp = request.urlopen(req)
        except Exception as em:
            print("EXCEPTION: " + str(em))

    def print_error(self):
        print(self.content, file=sys.stderr)

    def spread_the_word(self):
        self.send_to_slack()
        self.print_error()
        raise self.type
