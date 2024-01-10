"""Import module for YAML files."""
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError

from yml2block.rules import LintViolation, Level
from yml2block import validation


def read_yaml(file_path, lint_conf, verbose):
    """Read in a yaml file and convert it into a python dictionary structure."""
    with open(file_path, "r") as yml_file:
        yaml = YAML(typ="safe")
        try:
            data = yaml.load(yml_file)
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
