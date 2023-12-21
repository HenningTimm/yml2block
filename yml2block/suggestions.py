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
