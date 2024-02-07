"""Import module for YAML files."""
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError
# from ruamel.yaml.scalarstring import LiteralScalarString, FoldedScalarString, DoubleQuotedScalarString, SingleQuotedScalarString, PlainScalarString
# from ruamel.yaml.scalarint import ScalarInt
# from ruamel.yaml.scalarbool import ScalarBoolean

from yml2block.rules import LintViolation, Level
from yml2block import validation


# TODO: Implement custom constructor for ruamel yaml
# to get line and colum numbers for leafs in the yaml file
# https://stackoverflow.com/a/45717104


def read_yaml(file_path, lint_conf, verbose):
    """Read in a yaml file and convert it into a python dictionary structure."""
    with open(file_path, "r") as yml_file:
        # Use the ruamel.yaml round trip parser to get line and column info.
        # This is still considered safe: https://stackoverflow.com/a/71299116
        yaml_parser = YAML(typ="rt")
        try:
            data = yaml_parser.load(yml_file)
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
