import itertools as it
import subprocess
import tempfile
from pathlib import Path

import jinja2

from model import invoice as invoice_c
from model import organization


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

def cleanup_latex(output_path: Path):
    auxs = output_path.glob("*.aux")
    logs = output_path.glob("*.log")

    for file in it.chain(auxs, logs):
        file.unlink()

def cleanup_html(output_path: Path):
    pass