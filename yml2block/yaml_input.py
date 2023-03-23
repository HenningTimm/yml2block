"""Import module for YAML files.
"""
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError

from yml2block.rules import LintViolation
from yml2block import validation


def read_yaml(file_path, verbose, kwargs):
    """Read in a yaml file and convert it into a python dictionary structure."""
    with open(file_path, "r") as yml_file:
        yaml = YAML(typ="safe")
        try:
            data = yaml.load(yml_file)
            longest_row, file_lint_violations = validation.validate_yaml(data, verbose, kwargs)
        except DuplicateKeyError as dke:
            longest_row = 0
            # Raise error for duplicate keys
            file_lint_violations = [
                rules.LintViolation(
                    "ERROR",
                    "top_level_keywords_valid",
                    dke.problem,
                )
            ]
    return data, longest_row, file_lint_violations
