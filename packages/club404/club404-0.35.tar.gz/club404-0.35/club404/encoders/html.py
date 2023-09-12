
from club404.encoders import Encoder


class HtmlEncoder(Encoder):
    mime = "text/html"
    ext = [".htm", ".html", ".htmx"]
    def encode(data): return '<head></head><body>{}</body>'.format(data)
    def decode(data): return '{}'.format(data)

