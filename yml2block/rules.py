"""This file contains lints that can be selectively applied to yaml blocks.
"""
import re

from collections import Counter

# Note: The order of entries in this list defines the enforced order in the output file
# Note: These are referred to as top-level keywords.
permissible_keywords = ["metadataBlock", "datasetField", "controlledVocabulary"]
required_top_level_keywords = ["metadataBlock", "datasetField"]

required_keys = {
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

permissible_keys = {
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


def kw_order(kw):
    """Provide the canonical sort order expected by dataverse.

    Usage: `sorted(entries, key=kw_order)`
    """
    mdb_order = {key: i for i, key in enumerate(permissible_keywords)}
    return mdb_order[kw]


class LintViolation:
    def __init__(self, level, rule, message):
        self.level = level
        self.rule = rule
        self.message = message

    def __repr__(self):
        return f"{self.level} ({self.rule}): {self.message}"

    def __str__(self):
        return self.__repr__()


def unique_names(yaml_chunk, tsv_keyword):
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
                    "ERROR",
                    "unique_names",
                    f"Name '{name}' occurs {count} times. Names have to be unique.",
                )
            )
    return errors


def block_content_is_list(yaml_chunk):
    """Make sure that the yaml chunk is a list.

    block content level lint
    """
    if isinstance(yaml_chunk, list):
        return []
    else:
        return [
            LintViolation(
                "ERROR",
                "block_content_is_list",
                "Entry is not a list",
            )
        ]


def top_level_keywords_valid(keywords):
    """Make sure that the top-level keywords are spelled correctly and no additonal
    ones are present.

    top-level keyword level lint
    """
    unique_keys = set(keywords)
    if unique_keys == set(permissible_keywords):
        return []
    elif unique_keys == set(required_top_level_keywords):
        return []
    else:
        return [
            LintViolation(
                "ERROR",
                "top_level_keywords_valid",
                f"Keyword list '{keywords}' differs from '{permissible_keywords}' or '{required_top_level_keyword}'",
            )
        ]


def top_level_keywords_unique(keywords):
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
                "ERROR",
                "top_level_keywords_unique",
                f"Keyword list '{keywords}' contains duplicate keys.",
            )
        ]


def required_keys_present(list_item, tsv_keyword):
    """Make sure the keywords required for the current top-level item are present.

    second-level list entry lint
    """
    found_keys = list_item.keys()
    try:
        required = required_keys[tsv_keyword]
    except KeyError:
        return [
            LintViolation(
                "ERROR",
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
                "ERROR",
                "required_keys_present",
                f"List of required keys '{required}' and found keys '{found_keys}' differ.",
            )
        ]


def no_invalid_keys_present(list_item, tsv_keyword):
    """Make sure no invalid keys are present.

    second-level list entry lint
    """
    try:
        permissible = permissible_keys[tsv_keyword]
    except KeyError:
        return [
            LintViolation(
                "ERROR",
                "no_invalid_keys_present",
                f"Cannot check entry for invalid keyword '{tsv_keyword}'. Skipping entry.",
            )
        ]

    violations = []
    for key, value in list_item.items():
        if key not in permissible:
            violations.append(
                LintViolation(
                    "ERROR",
                    "no_invalid_keys_present",
                    f"Invalid key {key} present for {list_item} in block {tsv_keyword}.",
                )
            )
    return violations


def no_substructures_present(list_item, tsv_keyword):
    """Make sure list items do not contain dicts, tuples lists etc.

    second-level list entry lint
    """
    violations = []
    for key, value in list_item.items():
        if type(value) in (dict, tuple, list):
            violations.append(
                LintViolation(
                    "ERROR",
                    "no_substructures_present",
                    f"Key {key} in block {tsv_keyword} has a subtructure of type {type(value)}. Only strings, booleans, an numericals are allowed here.",
                )
            )
    return violations


def no_trailing_white_spaces(list_item, tsv_keyword):
    """Make sure the entries do not contain trailing white spaces.

    second-level list entry lint
    """
    entries_to_check = {
        "metadataBlock": ("name", "dataverseAlias"),
        "datasetField": ("name", "title", "description", "watermark", "fieldType", "parent", "metadatablock_id"),
        "controlledVocabulary": ("Value", "identifier"),
    }

    violations = []
    for entry in entries_to_check[tsv_keyword]:
        value = list_item[entry]
        if value and re.search(" +$", value):
            # Regex matches one or more spaces at the end of strings
            violations.append(
                LintViolation(
                    "ERROR",
                    "no_trailing_white_spaces",
                    f"The entry '{value}' has one or more trailing spaces.",
                )
            )
    return violations
