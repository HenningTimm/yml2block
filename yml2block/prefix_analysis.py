"""This module contains facilities to screen prefixes of metadata fields to detect typos.
"""
import os


def split_by_common_prefixes(keywords, threshold=3, verbose=True):
    """Split a list of keyword strings by their common prefixes.

    This has a worst case runtime of O(n^2) for the case where
    no prefix is shared.
    """
    identified_groups = []
    if verbose:
        print(f"Checking with threshold {threshold}")

    while keywords:
        selected_keyword = keywords.pop(0)
        current_group = [selected_keyword]
        current_prefix = None
        for kw in keywords:
            common_prefix = os.path.commonprefix((selected_keyword, kw))
            if verbose:
                print(
                    f"Checking keyword {kw} against selected keyword {selected_keyword} with current prefix {current_prefix}, found common prefix {common_prefix}"
                )
            if current_prefix is None and len(common_prefix) >= threshold:
                current_prefix = common_prefix
                current_group.append(kw)
            elif common_prefix == current_prefix:
                current_group.append(kw)
            elif current_prefix is not None and common_prefix.startswith(
                current_prefix
            ):
                current_group.append(kw)

        keywords = [kw for kw in keywords if kw not in current_group]
        identified_groups.append(current_group)
    if verbose:
        print("")
    return identified_groups
