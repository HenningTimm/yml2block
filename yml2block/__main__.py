#!/usr/bin/env python
"""Convert a yaml definition of a dataverse metadata schema into a metadata block understood by dataverse.

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

from yml2block.rules import Level


class ViolationsByFile:
    """Collect lint violations grouped by files."""

    def __init__(self):
        """Initialize empty violation collection."""
        self.violations = defaultdict(list)

    def add(self, file_path, violation):
        """Add a single violation for the given file path."""
        self.violations[file_path].append(violation)

    def extend(self, violation_list):
        """Extend the violation collection by an iterable of filename, violation tuples."""
        for file_path, violation in violation_list:
            self.add(file_path, violation)

    def extend_for(self, file_path, violation_list):
        """Extend violation list for a given file."""
        for violation in violation_list:
            self.add(file_path, violation)

    def items(self):
        """Get mapping of file names to violation lists."""
        yield from self.violations.items()

    def __len__(self):
        """Return number of files with errors."""
        return len(self.violations)

    def total_violations(self):
        """Return total number of violated lints."""
        return sum([len(vl) for vl in self.violations.entries()])


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
                    Level.WARNING,
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
                    Level.ERROR,
                    "guess_input_type",
                    f"Invalid file extension '{ext}'. Only .tsv and .yaml/.yml files are supported.",
                )
            ],
        )


@click.group()
def main():
    """Provide a central entry point for click group."""
    ...


@main.command()
@click.argument("file_path")
@click.option("--verbose", "-v", count=True, help="Print performed checks to stdout.")
def check(file_path, verbose):
    """Lint and validate a (yml or tsv) metadata block file.

    Loads the input file and performs a series of checks defined in the rules.py module.
    This call does not generate any output files.
    If error/ lint violations are detected, a non-zero return code is returned.
    If all lints pass, the return code is zero.

    Nore that this command can be used to provide a stand-alone linter.
    During conversion using the yml2block convert subcommand the same checks
    are also performed.
    """
    lint_violations = ViolationsByFile()

    if verbose:
        print(f"Checking input file: {file_path}\n\n")

    input_type, file_ext_violations = guess_input_type(file_path)
    lint_violations.extend_for(file_path, file_ext_violations)

    if input_type == "yaml":
        # This call invokes yaml validation internally
        _data, _longest_row, file_lint_violations = yaml_input.read_yaml(
            file_path, verbose
        )
    elif input_type in ("tsv", "csv"):
        data, tsv_parsing_violations = tsv_input.read_tsv(file_path)
        lint_violations.extend_for(file_path, tsv_parsing_violations)
        _longest_row, file_lint_violations = validation.validate_yaml(data, verbose)
    else:
        file_lint_violations = []

    lint_violations.extend_for(file_path, file_lint_violations)

    if len(lint_violations) == 0:
        if verbose:
            print("\nAll Checks passed!\n\n")
    else:
        for file_path, violations in lint_violations.items():
            print(file_path)
            print(f"A total of {len(violations)} lint(s) failed.")
            for violation in violations:
                print(violation)
        print("Errors detected. Conversion to TSV would not be possible.")
        sys.exit(1)


@main.command()
@click.argument("file_path")
@click.option("--verbose", "-v", count=True, help="Print performed checks to stdout.")
@click.option(
    "--outfile", "-o", nargs=1, help="Path to where the output file will be written."
)
def convert(file_path, verbose, outfile):
    """Convert a YML metadata block into a TSV metadata block.

    Reads in the provided Dataverse Metadata Block in YML format and converts it into
    a Dataverse-compliant TSV metadata block.
    For this, the input file is read and several QA checks and lints as defined in the
    roles.py module are applied. If all lints pass, the output file is written
    to the location specified via the out_path parameter. Per default, the .tsv file
    is placed next to the .yml input file.

    To only run the checks as a standalone linter, please use the yml2block check
    subcommand instead.
    """
    if outfile is None:
        path, _ext = os.path.splitext(file_path)
        outfile = f"{path}.tsv"

    if verbose:
        print(f"Checking input file: {file_path}\n\n")

    lint_violations = ViolationsByFile()

    input_type, file_ext_violations = guess_input_type(file_path)
    lint_violations.extend_for(file_path, file_ext_violations)

    if input_type == "yaml":
        # This call invokes YAML validation internally
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
        if input_type == "yaml":
            output.write_metadata_block(data, outfile, longest_row, verbose)
    else:
        for file_path, violations in lint_violations.items():
            print(file_path)
            print(f"A total of {len(violations)} lint(s) failed.")
            for violation in violations:
                print(violation)
        print("Errors detected. Could not convert to TSV.")
        sys.exit(1)


if __name__ == "__main__":
    main()
