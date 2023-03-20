"""This module contains facilities to screen prefixes of metadata fields to detect typos.

This module tries to guess, if minor typos are present in the attribute names.
We consider two attributes to be a likely to contain a typo, if they can be transformed
to be identical with few operations. Since we expect the most likely typos to be
replaced, missing, or transposed letters, we use the Damerau Levenshtein distance
to compute distances between texts.
The current heuristics are not able to guess all typos and can generate false positives.
Thus, all lints based on this module should only produce warnings instead of errors.

To estimate if an attribute contains an error, we group attributes by their shared prefixes,
which are a common way to group attributes as part of dataverse metadata schema files.
Based on this grouping by characteristic prefixes, we compare these prefixes.
The grouping is performed by the function split_bycommon_prefix and greedily groups
by the longest possible prefix. The exact rules are explained in the docstring of
that function.

Heuristics used to guess typos are applied in the function estimate typos.
Currently only a simple heuristic based on singletons is available, but additional
ones are planned for the future.
"""
import os
from jellyfish import damerau_levenshtein_distance as dl_dist


def split_by_common_prefixes(keywords, min_prefix_length=3, verbose=False):
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
        print(f"Checking with min_prefix_length {min_prefix_length}")

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

            if current_prefix is None and len(common_prefix) >= min_prefix_length:
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


def _singleton_heuristic(keyword_prefixes, dl_distance_threshold):
    typo_candidates = []
    singletons = [
        pref for pref, entries in keyword_prefixes.items() if len(entries) == 1
    ]
    for singleton_prefix in singletons:
        print(f"Singleton Prefix {singleton_prefix}")
        for prefix, entries in keyword_prefixes.items():
            print(f"  checking for {prefix}", end="")
            if prefix == singleton_prefix:
                # Skip the prefix itself
                print(" skipped (identity)")
                continue
            elif len(singleton_prefix) < len(prefix):
                # Skip prefixes that are longer than the selected singleton
                # since these cannot be mistyped versions of the same prefix
                print(" skipped for length")
                continue
            else:
                truncated_singleton_prefix = singleton_prefix[: len(prefix)]
                print(f" truncated to {truncated_singleton_prefix}", end="")
                computed_distance = dl_dist(truncated_singleton_prefix, prefix)
                print(f" with dl_dist == {computed_distance}")
                if computed_distance <= dl_distance_threshold:
                    typo_candidates.append(
                        (
                            {singleton_prefix: keyword_prefixes[singleton_prefix]},
                            {prefix: keyword_prefixes[prefix]},
                        ),
                    )
    return typo_candidates


def estimate_typos(
    keyword_prefixes, min_prefix_length=3, dl_distance_threshold=1, verbose=False
):
    """Run all typo estimation functions and return likely candidates for typos."""
    if verbose:
        print(f"Analysing keyword prefixes: {keyword_prefixes}")
        print(f"Searching for prefixes of length at least {min_prefix_length}")
        print(f"And a Damerau Levenshtein distance of at most {dl_distance_threshold}")

    typo_candidates = []
    split_keyword_prefixes = split_by_common_prefixes(
        keyword_prefixes, min_prefix_length, verbose
    )

    typo_candidates.extend(
        _singleton_heuristic(split_keyword_prefixes, dl_distance_threshold)
    )

    # TODO: Compute differences between larger groups as well.
    return typo_candidates
