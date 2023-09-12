import importlib

from club404.encoders.base import Encoder
from club404.encoders.csv import CsvEncoder
from club404.encoders.html import HtmlEncoder
from club404.encoders.json import JsonEncoder
from club404.encoders.text import TextEncoder
from club404.encoders.yaml import YamlEncoder


# Define common encoders
TEXT = TextEncoder()
HTML = HtmlEncoder()
JSON = JsonEncoder()
CSV = CsvEncoder()

# Register common encoders
Encoder.register(
    TEXT,
    HTML,
    CSV,
    JSON
)

# -----------------------------------------------------------------
# Load optional encoders only if the dependencies are installed
# -----------------------------------------------------------------
# Try and load the YAML encoder if `yaml` module found
YAML = None
try:
    YAML = YamlEncoder(importlib.import_module('yaml'))
    Encoder.register(YAML)
except ImportError:
    pass  # Module `yaml` not found...
