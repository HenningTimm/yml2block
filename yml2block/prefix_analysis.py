"""This module contains facilities to screen prefixes of metadata fields to detect typos.
"""
import os


def split_by_common_prefixes(keywords, threshold=3, verbose=False):
    """Split a list of keyword strings by their common prefixes.

    This has a worst case runtime of O(n^2) for the case where
    no prefix is shared.

    This approach greedily binds to the longest common prefix.
    This means that

      - "FooBarLong"
      - "FooBarShort"
      - "FooBarLonger"

    Would report two groups, one with the prefix "FooBarLong" containing
    "FooBarLong" and "FooBarLonger", the other group with prefix "FooBarShort"
    containing only the one item "FooBarShort".

    This behavor can result in false positive errors, when two or more entries
    share a slightly longer prefix by cnhance. For Example

      - "FooBarBaz"
      - "FooBarBest"
      - "FooBarTest1"

    Would report two groups, one with the prefix "FooBarB", even though semantically
    one could reasonably expect that these three entries fall into the same cathegory.
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
                    f"Checking keyword {kw} against selected keyword {selected_keyword} with "
                    f"current prefix {current_prefix}, found common prefix {common_prefix}"
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
                current_group.append(kw)

                # Filter keywords back out of the active list, that only share
                # a shorter common prefix. THis ensures that the longest possible prefix is chosen.
                current_prefix = common_prefix
                current_group = [
                    k for k in current_group if k.startswith(current_prefix)
                ]

        # Remove all keywords sharing a prefix with the selected reference keyword from the keywords list.
        keywords = [kw for kw in keywords if kw not in current_group]
        if current_prefix is None:
            current_prefix = selected_keyword
        identified_groups[current_prefix] = current_group

    if verbose:
        print("")

    return identified_groups
