"""This module provides a parser to convert a Dataverse TSV file into the same
dictionary-based representation used for YAML input.
"""
import csv
import io
import itertools

from yml2block.rules import LintViolation


def _identify_break_points(full_file):
    """Identify where to split the metadata block into its three subsections"""
    violations = []

    break_points = [i for i, l in enumerate(full_file) if l.startswith("#")]
    if len(break_points) == 3:
        split_blocks = (
            full_file[break_points[0] : break_points[1]],
            full_file[break_points[1] : break_points[2]],
            full_file[break_points[2] :],
        )
    elif len(break_points) == 2:
        split_blocks = (
            full_file[break_points[0] : break_points[1]],
            full_file[break_points[1] :],
            None,
        )
    else:
        split_block = full_file
        violations.append(
            LintViolation(
                "WARNING",
                "identify_break_points",
                "Unable to split TSV file into blocks. Check tsv file formatting.",
            )
        )
    return split_blocks, violations


def read_tsv(tsv_path):
    """Read in a Dataverse TSV metadata block file."""
    violations = []
    data = dict()

    with open(tsv_path, "r") as raw_file:
        full_file = raw_file.readlines()

    # Split metadata schema into blocks
    split_blocks, break_point_violations = _identify_break_points(full_file)
    violations.extend(break_point_violations)

    def _parse(block):
        """Parse a CSV block into a dictionary."""
        if block is None:
            return []
        # Wrap the joined lines in a StringIO buffer so it behaves
        # like a file an can be read by the csv DictReader
        joined = io.StringIO("\n".join(block))
        return csv.DictReader(joined, delimiter="\t")

    # Unpack each tsv-chunk of the metadata block into a list
    # of dictionaries.
    parsed_blocks = [_parse(block) for block in split_blocks]

    for row in itertools.chain(*parsed_blocks):
        # Each row corresponds to a line in the TSV file
        # unpacked into a dictionary with keys depending
        # on the part of the block identified by the top level keyword

        # Get the toplevel keyword from the first column of the TSV file
        # e.g. #metadataBlock, #datasetField, #controlledVocabulary
        toplevel_key_with_prefix = [
            entry for entry in row.keys() if entry is not None and entry.startswith("#")
        ][0]

        # For consistency with the yaml format
        toplevel_key = toplevel_key_with_prefix.lstrip("#")
        row_as_dict = dict()

        for key, value in row.items():
            if key is None:
                # These entries cannot be associated with a column header
                violations.append(
                    LintViolation("ERROR", "read_tsv", "Entry in headerless column")
                )
            elif key is toplevel_key_with_prefix:
                # Skip toplevel header identifiers. These columns are empty in
                # Dataverse TSV files
                continue
            else:
                # Copy all other entries into a new data structure for this row
                row_as_dict[key] = value

        # Initialize the entry for this toplevel keyword with an empty list
        if not (toplevel_key in data.keys()):
            data[toplevel_key] = []

        data[toplevel_key].append(row_as_dict)

    # Run top_level_keywords_valid here to make sure that the generated
    # data structure behaves as expected down the line

    # create dict that maps keywords to lists of dicts
    # Validate that nothing is in the leftover fields
    # Alert about whitespaces

    return data, violations
