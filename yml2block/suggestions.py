"""This file contains suggestions on how to fix certain lint violations."""

from difflib import SequenceMatcher


def identify_entry(list_item, tsv_keyword):
    """Get a human-readable identifier for the entry."""
    try:
        if tsv_keyword == "controlledVocabulary":
            return list_item["DatasetField"]
        else:
            return list_item["name"]
    except KeyError:
        return f"{list_item[:10]}[...]"


def fix_keywords_valid(keywords, permissible_keywords, required_keywords):
    """Suggest closest matching keyword."""
    additional_keywords = set(keywords) - set(permissible_keywords)
    message = []

    for kw in additional_keywords:
        matches = []
        for pkw in permissible_keywords:
            diff = SequenceMatcher(None, kw, pkw)
            matches.append((diff.ratio(), pkw))
        best_ratio, best_match = max(matches, key=lambda x: x[0])
        if best_ratio > 0.5:
            message.append(f"Invalid Keyword '{kw}'. Did you mean '{best_match}'?")
        else:
            message.append(
                f"Invalid Keyword '{kw}'. Valid Keywords are: '{permissible_keywords}'"
            )

    missing_keywords = set(required_keywords) - set(keywords)
    if missing_keywords:
        message.extend([f"Missing required keyword: '{kw}'" for kw in missing_keywords])
    return "; ".join(message)


def fix_keys_valid(key, list_item, tsv_keyword, permissible):
    """Find closest matching keyword name."""
    matches = []
    for pk in permissible:
        diff = SequenceMatcher(None, key, pk)
        matches.append((diff.ratio(), pk))

    best_ratio, best_match = max(matches, key=lambda x: x[0])

    name = identify_entry(list_item, tsv_keyword)
    message = [f"Invalid key '{key}' present for '{name}' in block '{tsv_keyword}'."]
    if best_ratio > 0.5:
        message.append(f"Did you mean '{best_match}'?")
    return " ".join(message)


def fix_required_keys_present(missing_keys, list_item, tsv_keyword):
    """Return list of missing keys."""
    name = identify_entry(list_item, tsv_keyword)
    return f"Missing keys '{missing_keys}' for '{name}' in block '{tsv_keyword}'."


def fix_identify_breaking_points(full_file, break_points):
    """Suggest fixes for too little or too many detected blocks."""
    match len(break_points):
        case 0:
            # No line starts with #
            # are you passing the right file?
            ...
        case 1:
            # Only one line starts with #
            # At least two blocks are required for a reasonable metadata schema
            ...
        case 2 | 3:
            # This case should never be reached, those files are fine
            # Raise an exception if I get here in error handling
            ...
        case _:
            # More than the required number of blocks is present.
            # Identify what is going on.
            ...
