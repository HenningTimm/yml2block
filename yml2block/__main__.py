#!/usr/bin/env python
"""This script converts a yaml definition of a dataverse metadata schema into
a metadata block understood by dataverse.

https://guides.dataverse.org/en/latest/admin/metadatacustomization.html
"""
import os
import sys
import click
from ruamel.yaml import YAML

from yml2block import validation
from yml2block import output


@click.command()
@click.argument("file_path")
@click.option("--verbose", "-v", count=True, help="Print performed checks to stdout.")
@click.option(
    "--outfile", "-o", nargs=1, help="Path to where the output file will be written."
)
@click.option(
    "--check",
    is_flag=True,
    help="Only check the yaml file and do not write any output.",
)
def main(file_path, verbose, outfile, check):

    if outfile is None:
        path, _ext = os.path.splitext(file_path)
        outfile = f"{path}.tsv"

    if verbose:
        print(f"Checking input file: {file_path}\n\n")

    with open(file_path, "r") as yml_file:
        yaml = YAML(typ="safe")
        data = yaml.load(yml_file)

        # data = load(yml_file.read(), Loader=CLoader)

    longest_row, lint_violations = validation.validate_yaml(data, verbose)

    if len(lint_violations) == 0:
        if verbose:
            print("\nAll Checks passed!\n\n")
        if not check:
            output.write_metadata_block(data, outfile, longest_row, verbose)
    else:
        print(f"A total of {len(lint_violations)} lint(s) failed.")
        for violation in lint_violations:
            print(violation)
        print("Errors detected. Could not convert to TSV.")
        sys.exit(1)


if __name__ == "__main__":
    main()
