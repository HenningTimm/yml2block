"""This file contains lints that can be selectively applied to yaml blocks.

This module contains rules that define a certain lint and return a
LintViolation object containing error severity, rule name, and
an error message.
"""

import re
import sys

from enum import IntEnum
from collections import Counter, defaultdict
from functools import partial

from yml2block import suggestions
from yml2block.datatypes import MDBlockList, MDBlockDict, MDBlockNode

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


class LintConfig:
    """Override lint functions with mofified versions.

    This is used to modify the error level of lints, e.g.
    making a certain lint a warning instead of an error.
    This is also used to sip lints.

    Internally, this config maps lint function objects to
    other lint function objects, which are modified,
    e.g. by usinf functools.partials or by applying a
    completely different function.
    """

    def __init__(self):
        """Create an empty config."""
        self.overrides = dict()

    @classmethod
    def from_cli_args(cls, error, warn, skip):
        """Create config using warning and skip lists from CLI."""
        conf = cls()

        for lint, apply_level in (
            [(e, conf.error) for e in error]
            + [(w, conf.warn) for w in warn]
            + [(s, conf.skip) for s in skip]
        ):
            try:
                lint_func = LINT_NAMES[lint]
                apply_level(lint_func)
            except KeyError:
                lint_names = "\n".join(LINT_NAMES.keys())
                print(f"Could not find lint with name or id '{lint}'")
                print(f"Valid lint names are:\n{lint_names}")
                sys.exit(1)
        return conf

    def get(self, lint):
        """Return an overridden lint, if present. Otherwise keep original lint."""
        try:
            return self.overrides[lint]
        except KeyError:
            return lint

    def add_override(self, lint, override):
        """Insert an override into the config."""
        self.overrides[lint] = override

    def error(self, lint):
        """Fix lint severity at ERROR."""
        self.add_override(lint, partial(lint, level=Level.ERROR))

    def warning(self, lint):
        """Fix lint severity at WARNING."""
        self.add_override(lint, partial(lint, level=Level.WARNING))

    def skip(self, lint):
        """Skip lint by overriding it with an identity function."""
        self.add_override(
            lint,
            # This function takes an arbitrary number of input values
            # and can thus be used as an identity function for any lint.
            lambda *x: [],
        )


class Level(IntEnum):
    """Provide numeric error levels."""

    NONE = 3
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

    def __init__(self, level, rule, message, line=None, column=None):
        """Create a new lint violation.

        Level defines the severity severity level of the error,
        e.g. WARNING or ERROR. Rule contains the rule name and
        an message contains a concise, human-readable error message.
        """
        self.level = level
        self.rule = rule
        self.message = message
        self.line = line
        self.column = column

    def __repr__(self):
        """Print as a log-style record."""
        if self.line:
            line_info = f"line {str(self.line)} "
        else:
            line_info = ""
        if self.column:
            # Put everything that is not an integer into single quotes
            if isinstance(self.column, int):
                col_info = f"column {self.column} "
            else:
                col_info = f"column '{str(self.column)}' "
        else:
            col_info = ""
        return f"[{self.level.name}] {line_info}{col_info}{self.rule}: {self.message}"

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
    occurrences = defaultdict(list)

    for item in yaml_chunk:
        item_name = item["name"].value
        names.update([item_name])
        occurrences[item_name].append(item)

    errors = []
    for name, count in names.items():
        if count > 1:
            occs = [f"line {o.line}" for o in occurrences[name]]
            errors.append(
                LintViolation(
                    level,
                    "unique_names",
                    f"Name '{name}' occurs {count} times: {', '.join(occs) if occs else ''}. Names have to be unique.",
                )
            )
    return errors


def unique_titles(yaml_chunk, tsv_keyword, level=Level.ERROR):
    """Make sure that each title in the block is only used once.

    block content level lint
    """
    if tsv_keyword not in ["datasetField"]:
        return []
    titles = Counter()
    occurrences = defaultdict(list)

    for item in yaml_chunk:
        # Use title parent tuple to allow identical titles
        # in different compound fields
        item_title = item["title"].value
        item_parent = item["parent"].value
        titles.update([(item_title, item_parent)])
        occurrences[item_title].append(item)

    errors = []
    for title, count in titles.items():
        if count > 1:
            occs = [f"line {o.line}" for o in occurrences[title]]
            errors.append(
                LintViolation(
                    level,
                    "unique_titles",
                    f"Title '{title}' occurs {count} times: {', '.join(occs) if occs else ''}. Titles should be unique.",
                )
            )
    return errors


def block_is_list(yaml_chunk, level=Level.ERROR):
    """Make sure that the yaml chunk is a list.

    block content level lint
    """
    if isinstance(yaml_chunk, list | MDBlockList):
        return []
    else:
        return [
            LintViolation(
                level,
                "block_is_list",
                "Entry is not a list",
                yaml_chunk.line,
                yaml_chunk.column,
            )
        ]


def keywords_valid(keywords, level=Level.ERROR):
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
                "keywords_valid",
                suggestions.fix_keywords_valid(
                    keywords, PERMISSIBLE_KEYWORDS, REQUIRED_TOP_LEVEL_KEYWORDS
                ),
            )
        ]


def keywords_unique(keywords, level=Level.ERROR):
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
                "keywords_unique",
                f"Keyword list '{keywords}' contains duplicate keys.",
            )
        ]


def keys_valid(list_item, tsv_keyword, level=Level.ERROR):
    """Make sure no invalid keys are present.

    block entry lint
    """
    try:
        permissible = PERMISSIBLE_KEYS[tsv_keyword]
    except KeyError:
        return [
            LintViolation(
                level,
                "keys_valid",
                f"Cannot check entry for invalid keyword '{tsv_keyword}'. Skipping entry.",
                list_item.line,
                list_item.column,
            )
        ]

    violations = []
    for key, value in list_item.items():
        if key not in permissible:
            violations.append(
                LintViolation(
                    level,
                    "keys_valid",
                    suggestions.fix_keys_valid(
                        key, list_item, tsv_keyword, permissible
                    ),
                    value.line,
                    value.column,
                )
            )
    return violations


def required_keys_present(list_item, tsv_keyword, level=Level.ERROR):
    """Make sure the keywords required for the current top-level item are present.

    block entry lint
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
                list_item.line,
                list_item.column,
            )
        ]
    # Assure all required keys are there
    missing_keys = set(required) - set(found_keys)
    if len(missing_keys) == 0:
        return []
    else:
        return [
            LintViolation(
                level,
                "required_keys_present",
                suggestions.fix_required_keys_present(
                    missing_keys, list_item, tsv_keyword
                ),
                list_item.line,
                list_item.column,
            )
        ]


def no_substructures(list_item, tsv_keyword, level=Level.ERROR):
    """Make sure list items do not contain dicts, tuples lists etc.

    block entry lint
    """
    violations = []
    for key, value in list_item.items():
        if type(value) in (dict, tuple, list):
            violations.append(
                LintViolation(
                    level,
                    "no_substructures",
                    f"Key {key} in block {tsv_keyword} has a subtructure of type {type(value)}. Only strings, booleans, an numericals are allowed here.",
                    list_item[key].line,
                    list_item[key].column,
                )
            )
    return violations


def no_trailing_spaces(list_item, tsv_keyword, level=Level.WARNING):
    """Make sure the entries do not contain trailing white spaces.

    block entry lint
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

    # This case occurs, when an invalid top level keyword is present
    # this is flagged by a specialized test above and does not need
    # to be handled here.
    if tsv_keyword not in entries_to_check:
        return []

    for entry in entries_to_check[tsv_keyword]:
        try:
            # Ensure 'value' is a string, as re.search requires
            # string input, not a numerical type like int.
            value = str(list_item[entry].value)
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
                    "no_trailing_spaces",
                    f"The entry '{value}' has one or more trailing spaces.",
                    list_item[entry].line,
                    list_item[entry].column,
                )
            )
    return violations


def nested_compound_metadata(list_item, tsv_keyword, level=Level.WARNING):
    """Screen for nested compound metadata (entries that are children, but allow multiple values).

    This variant checks for compound metadata that do not use a controled vocabulary.
    These are not offered via the dataverse UI and simpy do not work.

    block entry lint
    """

    violations = []

    if tsv_keyword != "datasetField":
        return []

    if (
        list_item["parent"].value is not None
        and list_item["allowmultiples"].value is True
        and list_item["allowControlledVocabulary"].value is False
    ):
        violations.append(
            LintViolation(
                level,
                "nested_compound_metadata",
                f"The entry '{list_item["name"]}' allows multiple entries in a nested field.",
                list_item["allowmultiples"].line,
                list_item["allowmultiples"].column,
            )
        )

    return violations


def nested_compound_metadata_controlled_vocab(
    list_item, tsv_keyword, level=Level.ERROR
):
    """Screen for nested compound metadata (entries that are children, but allow multiple values).

    This variant checks for compound metadata that do not use a controled vocabulary.
    These are not offered via the dataverse UI and simpy do not work.

    block entry lint
    """

    violations = []

    if tsv_keyword != "datasetField":
        return []

    if (
        list_item["parent"].value is not None
        and list_item["allowmultiples"].value is True
        and list_item["allowControlledVocabulary"].value is True
    ):
        violations.append(
            LintViolation(
                level,
                "nested_compound_metadata_controlled_vocab",
                f"The entry '{list_item["name"]}' allows multiple entries in a nested field.",
                list_item["allowmultiples"].line,
                list_item["allowmultiples"].column,
            )
        )

    return violations


LINT_NAMES = {
    "unique_names": unique_names,
    "b001": unique_names,
    "block_is_list": block_is_list,
    "b002": block_is_list,
    "unique_titles": unique_titles,
    "b003": unique_titles,
    "keywords_valid": keywords_valid,
    "k001": keywords_valid,
    "keywords_unique": keywords_unique,
    "k002": keywords_unique,
    "keys_valid": keys_valid,
    "e001": keys_valid,
    "required_keys_present": required_keys_present,
    "e002": required_keys_present,
    "no_substructures": no_substructures,
    "e003": no_substructures,
    "no_trailing_spaces": no_trailing_spaces,
    "e004": no_trailing_spaces,
    "nested_compound_metadata": nested_compound_metadata,
    "e005": nested_compound_metadata,
    "nested_compound_metadata_controlled_vocab": nested_compound_metadata_controlled_vocab,
    "e006": nested_compound_metadata_controlled_vocab,
}
