"""This file contains lints that can be selectively applied to yaml blocks.

This module contains rules that define a certain lint and return a
LintViolation object containing error severity, rule name, and
an error message.
"""
import re

from enum import Enum
from collections import Counter

# Note: The order of entries in this list defines the enforced order in the output file
# Note: These are referred to as top-level keywords.
PERMISSIBLE_KEYWORDS = ["metadataBlock", "datasetField", "controlledVocabulary"]
REQUIRED_TOP_LEVEL_KEYWORDS = ["metadataBlock", "datasetField"]

REQUIRED_KEYS = {
    "metadataBlock": ["name", "displayName"],
    "datasetField": [
        "name",
        "title",
        "description",
        "fieldType",
        "displayOrder",
        "advancedSearchField",
        "allowControlledVocabulary",
        "allowmultiples",
        "facetable",
        "displayoncreate",
        "required",
        "metadatablock_id",
    ],
    "controlledVocabulary": ["DatasetField", "Value"],
}

PERMISSIBLE_KEYS = {
    "metadataBlock": ["name", "dataverseAlias", "displayName", "blockURI"],
    "datasetField": [
        "name",
        "title",
        "description",
        "watermark",
        "fieldType",
        "displayOrder",
        "displayFormat",
        "advancedSearchField",
        "allowControlledVocabulary",
        "allowmultiples",
        "facetable",
        "displayoncreate",
        "required",
        "parent",
        "metadatablock_id",
        "termURI",
    ],
    "controlledVocabulary": [
        "DatasetField",
        "Value",
        "identifier",
        "displayOrder",
    ],
}


class Level(Enum):
    """Provide numeric error levels."""

    WARNING = 2
    ERROR = 1


def kw_order(kw):
    """Provide the canonical sort order expected by dataverse.

    Usage: `sorted(entries, key=kw_order)`
    """
    mdb_order = {key: i for i, key in enumerate(PERMISSIBLE_KEYWORDS)}
    return mdb_order[kw]


class LintViolation:
    """Class to model lint violations of different severity levels."""

    def __init__(self, level, rule, message):
        """Create a new lint violation.

        Level defines the severity severity level of the error,
        e.g. WARNING or ERROR. Rule contains the rule name and
        an message contains a concise, human-readable error message.
        """
        self.level = level
        self.rule = rule
        self.message = message

    def __repr__(self):
        """Print as a log-style record."""
        return f"{self.level} ({self.rule}): {self.message}"

    def __str__(self):
        """Pass on string representation."""
        return self.__repr__()


def unique_names(yaml_chunk, tsv_keyword, level=Level.ERROR):
    """Make sure that each name in the block is only used once.

    block content level lint
    """
    if tsv_keyword not in ["metadataBlock", "datasetField"]:
        return []
    names = Counter()
    for item in yaml_chunk:
        names.update([item["name"]])
    errors = []
    for name, count in names.items():
        if count > 1:
            errors.append(
                LintViolation(
                    level,
                    "unique_names",
                    f"Name '{name}' occurs {count} times. Names have to be unique.",
                )
            )
    return errors


def block_content_is_list(yaml_chunk, level=Level.ERROR):
    """Make sure that the yaml chunk is a list.

    block content level lint
    """
    if isinstance(yaml_chunk, list):
        return []
    else:
        return [
            LintViolation(
                level,
                "block_content_is_list",
                "Entry is not a list",
            )
        ]


def top_level_keywords_valid(keywords, level=Level.ERROR):
    """Ensure top-level keywords are spelled correctly and no additonal ones are present.

    top-level keyword level lint
    """
    unique_keys = set(keywords)
    if unique_keys == set(PERMISSIBLE_KEYWORDS):
        return []
    elif unique_keys == set(REQUIRED_TOP_LEVEL_KEYWORDS):
        return []
    else:
        return [
            LintViolation(
                level,
                "top_level_keywords_valid",
                f"Keyword list '{keywords}' differs from '{PERMISSIBLE_KEYWORDS}' or '{REQUIRED_TOP_LEVEL_KEYWORDS}'",
            )
        ]


def top_level_keywords_unique(keywords, level=Level.ERROR):
    """Make sure no keyword is specified twice.

    NOTE: This is most likely also enforced by the YAML parser,
    but adds an additional layer of security here.

    top-level keyword level lint
    """
    unique_keys = set(keywords)
    if len(unique_keys) == len(keywords):
        return []
    else:
        return [
            LintViolation(
                level,
                "top_level_keywords_unique",
                f"Keyword list '{keywords}' contains duplicate keys.",
            )
        ]


def required_keys_present(list_item, tsv_keyword, level=Level.ERROR):
    """Make sure the keywords required for the current top-level item are present.

    second-level list entry lint
    """
    found_keys = list_item.keys()
    try:
        required = REQUIRED_KEYS[tsv_keyword]
    except KeyError:
        return [
            LintViolation(
                level,
                "required_keys_present",
                f"Cannot check entry for invalid keyword '{tsv_keyword}'. Skipping entry.",
            )
        ]
    # Assure all required keys are there
    if len(set(required) - set(found_keys)) == 0:
        return []
    else:
        return [
            LintViolation(
                level,
                "required_keys_present",
                f"List of required keys '{required}' and found keys '{found_keys}' differ.",
            )
        ]


def no_invalid_keys_present(list_item, tsv_keyword, level=Level.ERROR):
    """Make sure no invalid keys are present.

    second-level list entry lint
    """
    try:
        permissible = PERMISSIBLE_KEYS[tsv_keyword]
    except KeyError:
        return [
            LintViolation(
                level,
                "no_invalid_keys_present",
                f"Cannot check entry for invalid keyword '{tsv_keyword}'. Skipping entry.",
            )
        ]

    violations = []
    for key, value in list_item.items():
        if key not in permissible:
            violations.append(
                LintViolation(
                    level,
                    "no_invalid_keys_present",
                    f"Invalid key {key} present for {list_item} in block {tsv_keyword}.",
                )
            )
    return violations


def no_substructures_present(list_item, tsv_keyword, level=Level.ERROR):
    """Make sure list items do not contain dicts, tuples lists etc.

    second-level list entry lint
    """
    violations = []
    for key, value in list_item.items():
        if type(value) in (dict, tuple, list):
            violations.append(
                LintViolation(
                    level,
                    "no_substructures_present",
                    f"Key {key} in block {tsv_keyword} has a subtructure of type {type(value)}. Only strings, booleans, an numericals are allowed here.",
                )
            )
    return violations


def no_trailing_white_spaces(list_item, tsv_keyword, level=Level.ERROR):
    """Make sure the entries do not contain trailing white spaces.

    second-level list entry lint
    """
    entries_to_check = {
        "metadataBlock": ("name", "dataverseAlias"),
        "datasetField": (
            "name",
            "title",
            "description",
            "watermark",
            "fieldType",
            "parent",
            "metadatablock_id",
        ),
        "controlledVocabulary": ("Value", "identifier"),
    }

    violations = []
    for entry in entries_to_check[tsv_keyword]:
        try:
            value = list_item[entry]
        except KeyError:
            # This case occurs, when a typo in one of the required
            # keywords is present. They can safely be skipped here,
            # since this error would also be detected in the rule
            # required_keys_present
            #
            # Verbosity option:
            # print(f"Could not check {entry} for {list_item}")
            continue
        if value and re.search(" +$", value):
            # Regex matches one or more spaces at the end of strings
            violations.append(
                LintViolation(
                    level,
                    "no_trailing_white_spaces",
                    f"The entry '{value}' has one or more trailing spaces.",
                )
            )
    return violations
