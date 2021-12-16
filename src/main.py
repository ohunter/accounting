import argparse
import itertools as it
import subprocess
import tempfile
from pathlib import Path
from pprint import pprint

import jinja2
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader

from filters import fmt_float, fmt_duration
from model import invoice as invoice_c, organization, desc_dict


def process(description: desc_dict) -> tuple[organization, list[invoice_c]]:
    org_ = organization(**description["organization"])

    invoices = [
        invoice_c(**invoice_dict) for invoice_dict in description["invoices"]
    ]

    pprint(org_)
    pprint(invoices)

    return org_, invoices


def latex(template: jinja2.Template, org: organization, invoice: invoice_c,
          output_path: Path):
    temp_dir = Path(tempfile.gettempdir())
    temp_file = temp_dir / f"{invoice.date}_{invoice.id}_{invoice.customer.name.split()[0]}.tex"
    temp_file.write_text(
        template.render(organization=org,
                        invoice=invoice,
                        customer=invoice.customer))

    subprocess.run([
        "pdflatex", "-interaction=batchmode", "-output-directory",
        str(output_path),
        str(temp_file)
    ])


def html(template: jinja2.Template, org: organization, invoice: invoice_c,
         output_path: Path):
    pass


def cleanup(output_path: Path):
    auxs = output_path.glob("*.aux")
    logs = output_path.glob("*.log")

    for file in it.chain(auxs, logs):
        file.unlink()


def parse_args():
    aparser = argparse.ArgumentParser()

    aparser.add_argument("files",
                         type=Path,
                         nargs="+",
                         metavar="FILE",
                         help="The invoice description")
    aparser.add_argument("-f",
                         "--formatting",
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
    aparser.add_argument("-o",
                         "--output",
                         type=Path,
                         default=Path(".").resolve(),
                         help="The output directory for the PDF")
    aparser.add_argument(
        "--template-path",
        type=Path,
        default=Path("./templates").resolve(),
        help="The path to the templates used to rended the invoices")

    return aparser.parse_args()


if __name__ == "__main__":
    parsed_args = parse_args()

    jenv = jinja2.Environment(block_start_string='\BLOCK{',
                              block_end_string='}',
                              variable_start_string='\VAR{',
                              variable_end_string='}',
                              trim_blocks=True,
                              autoescape=False,
                              loader=jinja2.FileSystemLoader(
                                  parsed_args.template_path))

    jenv.filters["fmt_float"] = fmt_float
    jenv.filters["fmt_duration"] = fmt_duration

    files = [
        process(yaml.load(file.read_text(), Loader=Loader))
        for file in parsed_args.files
    ]

    match parsed_args.formatting:
        case "latex":
            template = jenv.get_template("doc.tex.j2")
            for org, invoices in files:
                for invoice in invoices:
                    latex(template, org, invoice, parsed_args.output)

        case "html":
            template = jenv.get_template("doc.html.j2")
            for org, invoices in files:
                for invoice in invoices:
                    html(template, org, invoice, parsed_args.output)

    cleanup(parsed_args.output)
