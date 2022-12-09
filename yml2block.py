"""

https://guides.dataverse.org/en/latest/admin/metadatacustomization.html
"""
#!/usr/bin/env python
import click
from yaml import load, CLoader

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
        "termURI"
    ],
    "controlledVocabulary": [
        "DatasetField",
        "Value",
        "identifier",
        "displayOrder",
    ],
}


def validate_keywords(keywords, verbose):
    """Assure that the top-level keywords of the YAML file are well-behaved.
    """
    if verbose:
        print("Validating top-level keywords:", end=" ")
    # Prevent typos and additional entries
    assert all(kw in permissible_keywords for kw in keywords), "Invalid key"

    unique_keys = set(keywords)
    # Prevent duplicate entries
    assert len(unique_keys) == len(keywords), "Duplicate key"
    # Assure all entries are set
    # NOTE: This can be relaxed later to >0 and <=3 if we
    # are willing to skip over empty entries
    assert len(unique_keys) == 3, "Missing key"
    if verbose:
        print("SUCCESS!")


def validate_entry(yaml_chunk, tsv_keyword, verbose):
    if verbose:
        print(f"Validating entries for {tsv_keyword}:", end=" ")

    assert isinstance(yaml_chunk, list), "Entry is not a list"

    # Get these litsts once to prevent repeated dictionary accesses
    permissible = permissible_keys[tsv_keyword]
    required = required_keys[tsv_keyword]

    for item in yaml_chunk:
        found_keys = item.keys()
        # Assure all required keys are there
        assert len(set(required) - set(found_keys)) == 0, "Missing required key"

        for (key, value) in item.items():
            assert key in permissible, "Invalid key"
            assert not isinstance(value, dict), "Nested dictionaries are not allowed"

    if verbose:
        print("SUCCESS!")


def validate_yaml(data, verbose):
    validate_keywords(data.keys(), verbose)
    for kw, content in data.items():
        validate_entry(data[kw], kw, verbose)



@click.command()
@click.argument("file_path")
@click.option("--verbose", "-v", is_flag=True, help="Print performed checks to stdout.")
def main(file_path,verbose):
    with open(file_path, "r") as yml_file:
        data = load(yml_file.read(), Loader=CLoader)
    validate_yaml(data, verbose)


if __name__ == "__main__":
    main()
