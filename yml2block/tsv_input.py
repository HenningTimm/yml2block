"""This module provides a parser to convert a Dataverse TSV file into the same
dictionary-based representation used for YAML input.
"""
import csv
import io


def _trim_to_header(line, length):
    """Trim leading and trailing tabs from a tsv chunk to given nr of columns.

    The three parts of a Dataverse TSV file are themselves valid tsv.
    However, they all start with leadingall lines but the header start
    with a leading empty column and the shorter sections contain several
    empty trailing columns.
    """
    _leading_tab, *fields = line.strip("\n").split("\t")
    return "\t".join(fields[:length])


def read_tsv(tsv_path):
    with open(tsv_path, "r") as raw_file:
        mdb_lines = raw_file.readlines()

    full_file = open("computational_workflow.tsv", "r").readlines()
    break_points = [i for i, l in enumerate(full_file) if l.startswith("#")]
    split_blocks = (
        full_file[break_points[0] : break_points[1]],
        full_file[break_points[1] : break_points[2]],
        full_file[break_points[2] :],
    )

    def _parse(block):
        """Parse a CSV block into a dictionary."""
        # Wrap the joined lines in a StringIO buffer so it behaves
        # like a file an can be read by the csv DictReader
        joined = io.StringIO("\n".join(block))
        return csv.DictReader(joined, delimiter="\t")

    md_fields, ds_fields, vocab_fields = [_parse(block) for block in split_blocks]

    def print_dict(d):
        for r in d:
            print(r)

    print_dict(md_fields)
    print_dict(ds_fields)
    print_dict(vocab_fields)

    # clip off keyword

    # Run top_level_keywords_valid here to make sure that the generated
    # data structure behaves as expected down the line

    # create dict that maps keywords to lists of dicts
    # Validate that nothing is in the leftover fields
    # Alert about whitespaces
