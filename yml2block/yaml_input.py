"""Import module for YAML files."""

from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError

from yml2block.rules import LintViolation, Level
from yml2block.datatypes import MDBlockList, MDBlockDict, MDBlockNode
from yml2block import validation


def to_md_block_types(data):
    """This function takes a ruamel YAML structure and wraps its
    content into custom types that support annotation with line and column
    numbers to be compatible with the tsv input.
    """
    match data:
        case dict():
            return MDBlockDict(
                {key: to_md_block_types(val) for key, val in data.items()},
                line=data.lc.line,
                column=data.lc.col,
            )
        case list():
            return MDBlockList(
                [to_md_block_types(d) for d in data],
                line=data.lc.line,
                column=data.lc.col,
            )
        case _:
            return MDBlockNode(data)


def read_yaml(file_path, lint_conf, verbose):
    """Read in a yaml file and convert it into a python dictionary structure."""
    with open(file_path, "r") as yml_file:
        # Use the ruamel.yaml round trip parser to get line and column info.
        # This is still considered safe: https://stackoverflow.com/a/71299116
        yaml_parser = YAML(typ="rt")
        try:
            data = yaml_parser.load(yml_file)
            data = to_md_block_types(data)
            longest_row, file_lint_violations = validation.validate_yaml(
                data, lint_conf, verbose
            )
        except DuplicateKeyError as dke:
            longest_row = 0
            data = None
            # Raise error for duplicate keys
            file_lint_violations = [
                LintViolation(
                    Level.ERROR,
                    "top_level_keywords_valid",
                    f"ruamel.yaml says '{dke.problem}'",
                )
            ]

    return data, longest_row, file_lint_violations
