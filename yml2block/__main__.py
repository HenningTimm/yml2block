#!/usr/bin/env python
"""This script converts a yaml definition of a dataverse metadata schema into
a metadata block understood by dataverse.

https://guides.dataverse.org/en/latest/admin/metadatacustomization.html
"""
import os
import sys
import click

from collections import defaultdict

from yml2block import validation
from yml2block import output
from yml2block import rules
from yml2block import tsv_input
from yml2block import yaml_input


class ViolationsByFile:
    def __init__(self):
        self.violations = defaultdict(list)

    def add(self, file_path, violation):
        self.violations[file_path].append(violation)

    def extend(self, violation_list):
        for file_path, violation in violation_list:
            self.add(file_path, violation)

    def extend_for(self, file_path, violation_list):
        for violation in violation_list:
            self.add(file_path, violation)

    def items(self):
        yield from self.violations.items()

    def __len__(self):
        return len(self.violations)


def guess_input_type(input_path):
    """Guess the input type from the file name."""
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    if ext == ".tsv":
        return ("tsv", [])
    elif ext == ".csv":
        return (
            "csv",
            [
                rules.LintViolation(
                    "WARNING",
                    "guess_input_type",
                    f"Invalid file extension '{ext}'. Will be treated as tsv. Currently non-tab separators are not supported.",
                )
            ],
        )
    elif ext in (".yml", ".yaml"):
        return ("yaml", [])
    else:
        return (
            False,
            [
                rules.LintViolation(
                    "ERROR",
                    "guess_input_type",
                    f"Invalid file extension '{ext}'. Only .tsv and .yaml/.yml files are supported.",
                )
            ],
        )


@click.group()
def main():
    ...


@main.command()
@click.argument("file_path")
@click.option("--verbose", "-v", count=True, help="Print performed checks to stdout.")
@click.option(
    "--outfile", "-o", nargs=1, help="Path to where the output file will be written."
)
@click.option(
    "--check",
    is_flag=True,
    help="Only check the metadata block (yml or tsv) file and do not write any output.",
)
def check(file_path, verbose, outfile, check):
    if outfile is None:
        path, _ext = os.path.splitext(file_path)
        outfile = f"{path}.tsv"

    if verbose:
        print(f"Checking input file: {file_path}\n\n")

    lint_violations = ViolationsByFile()

    input_type, file_ext_violations = guess_input_type(file_path)
    lint_violations.extend_for(file_path, file_ext_violations)

    if input_type == "yaml":
        data, longest_row, file_lint_violations = yaml_input.read_yaml(
            file_path, verbose
        )
    elif input_type in ("tsv", "csv"):
        data, tsv_parsing_violations = tsv_input.read_tsv(file_path)
        lint_violations.extend_for(file_path, tsv_parsing_violations)
        longest_row, file_lint_violations = validation.validate_yaml(data, verbose)
    else:
        file_lint_violations = []
        longest_row = 0

    lint_violations.extend_for(file_path, file_lint_violations)

    if len(lint_violations) == 0:
        if verbose:
            print("\nAll Checks passed!\n\n")
        if (not check) and (input_type == "yaml"):
            output.write_metadata_block(data, outfile, longest_row, verbose)
    else:
        print(f"A total of {len(lint_violations)} lint(s) failed.")
        for file_path, violation in lint_violations.items():
            print(file_path, violation)
        print("Errors detected. Could not convert to TSV.")
        sys.exit(1)


@main.command()
@click.argument("file_path")
@click.option("--verbose", "-v", count=True, help="Print performed checks to stdout.")
@click.option(
    "--outfile", "-o", nargs=1, help="Path to where the output file will be written."
)
@click.option(
    "--check",
    is_flag=True,
    help="Only check the metadata block (yml or tsv) file and do not write any output.",
)
def convert(file_path, verbose, outfile, check):
    if outfile is None:
        path, _ext = os.path.splitext(file_path)
        outfile = f"{path}.tsv"

    if verbose:
        print(f"Checking input file: {file_path}\n\n")

    lint_violations = ViolationsByFile()

    input_type, file_ext_violations = guess_input_type(file_path)
    lint_violations.extend_for(file_path, file_ext_violations)

    if input_type == "yaml":
        data, longest_row, file_lint_violations = yaml_input.read_yaml(
            file_path, verbose
        )
    elif input_type in ("tsv", "csv"):
        data, tsv_parsing_violations = tsv_input.read_tsv(file_path)
        lint_violations.extend_for(file_path, tsv_parsing_violations)
        longest_row, file_lint_violations = validation.validate_yaml(data, verbose)
    else:
        file_lint_violations = []
        longest_row = 0

    lint_violations.extend_for(file_path, file_lint_violations)

    if len(lint_violations) == 0:
        if verbose:
            print("\nAll Checks passed!\n\n")
        if (not check) and (input_type == "yaml"):
            output.write_metadata_block(data, outfile, longest_row, verbose)
    else:
        print(f"A total of {len(lint_violations)} lint(s) failed.")
        for file_path, violation in lint_violations.items():
            print(file_path, violation)
        print("Errors detected. Could not convert to TSV.")
        sys.exit(1)


if __name__ == "__main__":
    main()
