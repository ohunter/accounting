import pdb
from enum import Enum
from pathlib import Path

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader

from model import desc_dict
from model import invoice as invoice_c
from model import organization


class Format(str, Enum):
    latex="LaTeX"
    html="HTML"

class Language(str, Enum):
    no="no"
    en="en"

def process_files(files: list[Path]) -> list[tuple[organization, list[invoice_c]]]:
    out: list[tuple[organization, list[invoice_c]]] = []

    for file in files:
        data: desc_dict = yaml.load(file.read_text(), Loader=Loader)
        out.append((
            organization(**data["organization"]),[
        invoice_c(**invoice_dict) for invoice_dict in data["invoices"]
        ]))

    return out
