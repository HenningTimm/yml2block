"""This module provides a parser to convert a Dataverse TSV file into the same
dictionary-based representation used for YAML input.
"""
import csv
import io
import itertools

from yml2block.rules import LintViolation

# def _trim_to_header(line, length):
#     """Trim leading and trailing tabs from a tsv chunk to given nr of columns.

#     The three parts of a Dataverse TSV file are themselves valid tsv.
#     However, they all start with leadingall lines but the header start
#     with a leading empty column and the shorter sections contain several
#     empty trailing columns.
#     """
#     _leading_tab, *fields = line.strip("\n").split("\t")
#     return "\t".join(fields[:length])


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
    violations = []

    with open(tsv_path, "r") as raw_file:
        full_file = raw_file.readlines()

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

    md_fields, ds_fields, vocab_fields = [_parse(block) for block in split_blocks]
    data = dict()

    def print_dict(d):
        for r in d:
            print(r)

    # print_dict(md_fields)
    # print_dict(ds_fields)
    # print_dict(vocab_fields)

    for row in itertools.chain(*(md_fields, ds_fields, vocab_fields)):
        toplevel_key_with_hash = [
            entry for entry in row.keys() if entry is not None and entry.startswith("#")
        ][0]
        toplevel_key = toplevel_key_with_hash.lstrip("#")
        row_as_dict = dict()

        for key, value in row.items():
            if key is None:
                violations.append(
                    LintViolation("ERROR", "read_tsv", "Entry in headerless column")
                )
            elif key is toplevel_key_with_hash:
                continue
            else:
                row_as_dict[key] = value
        if not (toplevel_key in data.keys()):
            data[toplevel_key] = []
        data[toplevel_key].append(row_as_dict)

    print(data)
    # clip off keyword

    # Run top_level_keywords_valid here to make sure that the generated
    # data structure behaves as expected down the line

    # create dict that maps keywords to lists of dicts
    # Validate that nothing is in the leftover fields
    # Alert about whitespaces

    return data, violations
