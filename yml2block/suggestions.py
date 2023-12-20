"""This file contains suggestions on how to fix certain lint violations."""

from difflib import SequenceMatcher
from yml2block import rules


def fix_keywords_valid(keywords, permissible_keywords, required_keywords):
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
