"""This module provides a parser to convert a Dataverse TSV file into the same
dictionary-based representation used for YAML input.
"""


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
    with open(md_block_csv, "r") as raw_file:
        mdb_lines = raw_file.readlines()

    # Extract all keyword lines
    keyword_lines = [line for line in mdb_lines if line.startswith("#")]

    kw_indices = {}
    for kw_line in keyword_lines:
        mdb_keyword, *header_fields = kw_line.strip("\n\t").split("\t")

        # Some header fields in the metadata blocks supplied by the
        # Dataverse repo have additional whitespaces.
        # most notably the fieldType column has a leading space
        # in most metadata blocks. This stripping weakens the lint,
        # but ensures that the files provided by dataverse check out
        # as valid.
        header_fields = [hf.strip(" ") for hf in header_fields]

        # Keep the position of the keyword in the lines
        # to later split the blocks.
        kw_indices[mdb_keyword] = mdb_lines.index(kw_line)

    # Compute boundaries between different sections (name, fields, vocab)
    # of the metadata block
    ds_fields_start = kw_indices["#datasetField"] + 1
    if "#controlledVocabulary" in kw_indices:
        ds_fields_stop = kw_indices["#controlledVocabulary"]
    else:
        # In case no controlled vocab was defined, read to the end
        ds_fields_stop = None
