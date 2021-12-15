import argparse
from pprint import pprint

import jinja2
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader

if __name__ == "__main__":
    aparser = argparse.ArgumentParser()

    aparser.add_argument("-o",
                         "--output-format",
                         type=str,
                         choices=["latex", "html"],
                         required=True,
                         help="The output format of the invoice")
    aparser.add_argument("-l",
                         "--language",
                         type=str,
                         choices=["no", "en"],
                         default="en",
                         help="The language used in the outputted invoice")

    parsed_args = aparser.parse_args()

    pprint(parsed_args)