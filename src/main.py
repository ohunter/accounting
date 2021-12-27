from datetime import timedelta
import pdb
from collections import defaultdict
from pathlib import Path
from typing import Mapping
from pprint import pprint

import jinja2
import typer

from model import summary
from filters import fmt_duration, fmt_float
from invoice import cleanup_html, cleanup_latex, html, latex
from typer_options import Format, Language, process_files

app = typer.Typer()

@app.command("invoice")
def gen_invoice(
    formatting: Format = typer.Option(Format.latex, "-f", case_sensitive=False, help="The output format for the generated invoices"),
    language: Language = typer.Option(Language.no, '-l', case_sensitive=False, help="The language used by the generated invoices"),
    output: Path = typer.Option(..., "--output", "-o"),
    template_path: Path = typer.Option(..., "--template-path", "-t"),
    files: list[Path] = typer.Argument(...)
):

    jenv = jinja2.Environment(block_start_string='\\BLOCK{',
                              block_end_string='}',
                              variable_start_string='\\VAR{',
                              variable_end_string='}',
                              trim_blocks=True,
                              autoescape=False,
                              loader=jinja2.FileSystemLoader(template_path))

    assert getattr(jenv, "filters") and isinstance(getattr(jenv, "filters"), Mapping)
    getattr(jenv, "filters")["fmt_float"] = fmt_float
    getattr(jenv, "filters")["fmt_duration"] = fmt_duration

    processed = process_files(files)

    match formatting:
        case Format.latex:
            template = jenv.get_template("doc.tex.j2")
            for org, invoices in processed:
                for invoice in invoices:
                    latex(template, org, invoice, output)

            cleanup_latex(output)
        case Format.html:
            template = jenv.get_template("doc.html.j2")
            for org, invoices in processed:
                for invoice in invoices:
                    html(template, org, invoice, output)

            cleanup_html(output)

@app.command("summary")
def gen_summary(files: list[Path] = typer.Argument(...)):
    processed = process_files(files)

    orgs = defaultdict(lambda: defaultdict(list[summary]))

    # Gather the various invoices per company and separate them by year
    for org, invoices in processed:
        for invoice in invoices:
            orgs[org.name][invoice.date.year].extend(invoice.summaries)
    
    # Generate the yearly summary per org
    summaries = {
        org: {
            year: {
                "Hourly": sum((x.total for x in summaries if x.type == "HOUR")),
                "Drives": sum((x.total for x in summaries if x.type == "DRIVE")),
                "Expenses": sum((x.total for x in summaries if x.type == "EXPENSE")),
            }
            for year, summaries in years.items()
        }
        for org, years in orgs.items()
    }

    pprint(summaries)

if __name__ == "__main__":
    app()
