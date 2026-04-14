"""Genre matching helpers used by retrieval and scoring."""


def tokenize_genre(value: str) -> set[str]:
    """Split a genre-like label into normalized tokens for partial matching."""
    normalized = value.replace("-", " ").replace("/", " ").strip().lower()
    return {token for token in normalized.split() if token}


def lead_genre_token_similarity(candidate: str, profile: str) -> float:
    """Return the token-overlap score between a candidate and profile lead genre."""
    candidate_tokens = tokenize_genre(candidate)
    profile_tokens = tokenize_genre(profile)
    if not candidate_tokens or not profile_tokens:
        return 0.0
    union = candidate_tokens.union(profile_tokens)
    if not union:
        return 0.0
    return round(len(candidate_tokens.intersection(profile_tokens)) / len(union), 6)
