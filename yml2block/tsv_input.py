"""This module provides a parser to convert a Dataverse TSV file into the same
dictionary-based representation used for YAML input.
"""

import csv
import io
import itertools

from yml2block.rules import LintViolation, Level
from yml2block.datatypes import MDBlockList, MDBlockDict, MDBlockNode


def _identify_break_points(full_file):
    """Identify where to split the metadata block into its three subsections"""
    violations = []

    # Split along lines starting with '#'
    break_points = [i for i, line in enumerate(full_file) if line.startswith("#")]
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
        # TODO: suggest better fix for this
        split_blocks = full_file
        violations.append(
            LintViolation(
                Level.WARNING,
                "identify_break_points",
                "Unable to split TSV file into blocks. Check tsv file formatting.",
            )
        )
    return split_blocks, violations


def read_tsv(tsv_path):
    """Read in a Dataverse TSV metadata block file and convert it into a python dictionary structure."""
    violations = []
    data = MDBlockDict()

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
    parsed_blocks = [
        zip(_parse(block), itertools.repeat(offset))
        for offset, block in enumerate(split_blocks, 1)
    ]

    for line_no, (row, offset) in enumerate(itertools.chain(*parsed_blocks), 1):
        # Each row corresponds to a content line in the TSV file
        # unpacked into a dictionary with keys depending
        # on the part of the block identified by the top level keyword

        # Get the toplevel keyword from the first column of the TSV file
        # e.g. #metadataBlock, #datasetField, #controlledVocabulary
        toplevel_key_with_prefix = [
            entry for entry in row.keys() if entry is not None and entry.startswith("#")
        ][0]

        # For consistency with the yaml format
        toplevel_key = toplevel_key_with_prefix.lstrip("#")

        # print(f"{line_no} + {offset} = {line_no + offset}", row)
        row_as_dict = MDBlockDict()
        offset_line_no = line_no + offset
        row_as_dict.line = offset_line_no
        row_as_dict.column = None

        for key, value in row.items():
            if key is None:
                # These entries cannot be associated with a column header
                violations.append(
                    LintViolation(Level.ERROR, "read_tsv", "Entry in headerless column")
                )
            elif not key and not value:
                # Skip empty entries ('': '') that result from the empty columns in
                # the TSV file used to pad all lines to the same length.
                continue
            elif key is toplevel_key_with_prefix:
                # Skip toplevel header identifiers. These columns are empty in
                # Dataverse TSV files
                continue
            else:
                # Copy all other entries into a new data structure for this row
                row_as_dict[key] = MDBlockNode(value, line=offset_line_no)

        # Initialize the entry for this toplevel keyword with an empty list
        if toplevel_key not in data.keys():
            block_list = MDBlockList()
            block_list.line = line_no
            block_list.column = None
            data[toplevel_key] = block_list

        data[toplevel_key].append(row_as_dict)

    print(data)
    return data, violations
