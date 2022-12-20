"""This file contains lints that can be selectively applied to yaml blocks.
"""
from collections import Counter


# Note: The order of entries in this list defines the enforced order in the output file
# Note: These are referred to as top-level keywords.
permissible_keywords = ["metadataBlock", "datasetField", "controlledVocabulary"]

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


def unique_names(yaml_chunk):
    """Make sure that each name in the block is only used once.

    block content level lint
    """
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
                    f"Name {name} occurs {count} times. Names have to be unique.",
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
        return [LintViolation("ERROR", "block_content_is_list", "Entry is not a list",)]
