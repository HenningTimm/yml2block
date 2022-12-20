#!/usr/bin/env python
"""This script converts a yaml definition of a dataverse metadata schema into
a metadata block understood by dataverse.

https://guides.dataverse.org/en/latest/admin/metadatacustomization.html
"""
import os
import sys
import click
from yaml import load, CLoader

import rules


def validate_keywords(keywords, verbose):
    """Assure that the top-level keywords of the YAML file are well-behaved.

    Fail with an assertion if they do not comply."""
    if verbose:
        print("Validating top-level keywords:", end=" ")
    # Prevent typos and additional entries
    violations = []
    for lint in [
        rules.top_level_keywords_valid,
        rules.top_level_keywords_unique,
        rules.top_level_keywords_complete,
    ]:
        violations.extend(lint(keywords))

    if verbose and len(violations) == 0:
        print("SUCCESS!")
    if violations:
        print("FAILURE! Detected violations:")
        print("\n".join([str(v) for v in violations]))


def validate_entry(yaml_chunk, tsv_keyword, verbose):
    """Validate a record, based on its type.

    Check that all required keys are there.
    Fail with an assertion if a violation is detected.
    """
    if verbose:
        print(f"Validating entries for {tsv_keyword}:", end=" ")

    violations = []
    for lint in (rules.block_content_is_list,):
        violations.extend(lint(yaml_chunk))

    # Get these litsts once to prevent repeated dictionary accesses
    permissible = rules.permissible_keys[tsv_keyword]
    required = rules.required_keys[tsv_keyword]

    longest_row = 0

    if tsv_keyword in ["metadataBlock", "datasetField"]:
        if v := rules.unique_names(yaml_chunk):
            violations.extend(v)

    for item in yaml_chunk:
        found_keys = item.keys()
        # Assure all required keys are there
        assert len(set(required) - set(found_keys)) == 0, "Missing required key"

        for (key, value) in item.items():
            assert key in permissible, "Invalid key"
            assert not isinstance(value, dict), "Nested dictionaries are not allowed"

        # Compute the highest number of columns in the block
        row_length = len(item.keys()) if tsv_keyword == "metadataBlock" else len(item.keys()) + 1
        longest_row = max(longest_row, row_length)

    if verbose and len(violations) == 0:
        print("SUCCESS!")
    if violations:
        print("FAILURE! Detected violations:")
        print("\n".join([str(v) for v in violations]))

    return longest_row


def write_metadata_block(yml_metadata, output_path, verbose):
    """Write a validated nested dictionary of yml_metadata into
    a dataverse tsv metadata block file.
    """
    if verbose:
        print(f"Writing output file to: {output_path}")

    with open(output_path, "w") as out_file:
        for bn, content in yml_metadata.items():
            block_name = f"#{bn}"
            block_headers = []
            block_lines = []

            for block_line in content:
                new_line = [""]

                for key, value in block_line.items():
                    if key not in block_headers:
                        block_headers.append(key)

                    # TODO: Consider screening for True, False, None
                    # before and replace them.
                    if value is True:
                        # This catches all value that YAML considers truthy
                        # and are `true`
                        new_line.append("TRUE")
                    elif value is False:
                        # This catches all value that YAML considers truthy
                        # and are `false`
                        new_line.append("FALSE")
                    elif value is None:
                        # This catches empty values, which yaml reports
                        # as a Python None
                        new_line.append("")
                    elif str(value):
                        # This could be more specific using int() and float()
                        # The conversion of `value` to a string happens to
                        # catch `0` values, which evaluate to `False` under
                        # the python `bool()` function.
                        new_line.append(str(value))
                    else:
                        # This should never happend
                        print(f"Invalid entry '{value}'", file=sys.stderr)
                # TODO: Pad new lines to longest column
                block_lines.append("\t".join(new_line))
            block_header = "\t".join([block_name] + block_headers)

            print(block_header, file=out_file)
            print("\n".join(block_lines), file=out_file)


def validate_yaml(data, verbose):
    """Check if the given yaml file is valid.
    Underlying checks will fail with an assertion if they don't.
    """
    validate_keywords(data.keys(), verbose)
    longest_row = 0
    for kw, content in data.items():
        block_row_max = validate_entry(data[kw], kw, verbose)
        longest_row = max(longest_row, block_row_max)
    if verbose:
        print("\nAll Checks passed!\n\n")
    return longest_row


@click.command()
@click.argument("file_path")
@click.option("--verbose", "-v", is_flag=True, help="Print performed checks to stdout.")
@click.option(
    "--outfile", "-o", nargs=1, help="Path to where the output file will be written."
)
def main(file_path, verbose, outfile):
    if outfile is None:
        path, _ext = os.path.splitext(file_path)
        outfile = f"{path}.tsv"

    if verbose:
        print(f"Checking input file: {file_path}\n\n")

    with open(file_path, "r") as yml_file:
        data = load(yml_file.read(), Loader=CLoader)

    print(f"Longest row has {validate_yaml(data, verbose)} columns")

    write_metadata_block(data, outfile, verbose)


if __name__ == "__main__":
    main()
