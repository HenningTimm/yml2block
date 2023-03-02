"""This module contains facilities to screen prefixes of metadata fields to detect typos.
"""
import os


def split_by_common_prefixes(keywords, threshold=3, verbose=False):
    """Split a list of keyword strings by their common prefixes.

    This has a worst case runtime of O(n^2) for the case where
    no prefix is shared.

    Note that currently this approach greedily binds to the first prefix.
    This means that

      - "FooBarLong"
      - "FooBarShort"
      - "FooBarLonger"

    Would report one group containing all three keywords with the common
    prefix "FooBar". The other possible solution returning two groups
    (one containing "FooBarLong" and "FooBarLonger" with a prefix "FooBarLong"
    and the second group containing only "FooBarShort") can currebtly be achieved
    using a threshold.

    However, to identify typos it would be helpful to bind to the longest
    prefix instead.
    """
    identified_groups = {}
    if verbose:
        print(f"Checking with threshold {threshold}")

    while keywords:
        # Pick the first entry of keywords as the reference entry and remove it
        # from the list. This ensures, that this loop terminates after at most n
        # iterations.
        selected_keyword = keywords.pop(0)
        current_group = [selected_keyword]
        current_prefix = None

        for kw in keywords:
            # Compute longest shared prefix between the selected reference keyword
            # and the current keyword.
            common_prefix = os.path.commonprefix((selected_keyword, kw))
            if verbose:
                print(
                    f"Checking keyword {kw} against selected keyword {selected_keyword} with current prefix {current_prefix}, found common prefix {common_prefix}"
                )

            if current_prefix is None and len(common_prefix) >= threshold:
                # The first shared prefix was detected.
                current_prefix = common_prefix
                current_group.append(kw)
            elif common_prefix == current_prefix:
                # The current prefix is matched exactly
                current_group.append(kw)
            elif current_prefix is not None and common_prefix.startswith(
                current_prefix
            ):
                # The detected common prefix is a superset of the expected prefix.

                current_prefix = common_prefix
                current_group.append(kw)
                current_group = [
                    k for k in current_group if k.startswith(current_prefix)
                ]

        print()
        # Remove all keywords sharing a prefix with the selected reference keyword from the keywords list.
        keywords = [kw for kw in keywords if kw not in current_group]
        if current_prefix is None:
            current_prefix = selected_keyword
        identified_groups[current_prefix] = current_group

    if verbose:
        print("")

    return identified_groups
