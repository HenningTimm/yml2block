import sys


def write_metadata_block(yml_metadata, output_path, longest_line, verbose):
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

                # Pad new lines to longest column
                if len(new_line) < longest_line:
                    new_line.extend([""] * (longest_line - len(new_line)))

                block_lines.append("\t".join(new_line))

            block_header_fragments = [block_name] + block_headers
            # Pad header to longest column
            if len(block_header_fragments) < longest_line:
                block_header_fragments.extend(
                    [""] * (longest_line - len(block_header_fragments))
                )
            block_header = "\t".join(block_header_fragments)

            print(block_header, file=out_file)
            print("\n".join(block_lines), file=out_file)
