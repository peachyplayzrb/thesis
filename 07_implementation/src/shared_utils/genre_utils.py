"""Genre matching helpers shared by retrieval and scoring stages."""


def tokenize_genre(value: str) -> set[str]:
    """Tokenize genre-like strings for robust partial matching."""
    normalized = value.replace("-", " ").replace("/", " ").strip().lower()
    return {token for token in normalized.split() if token}


def lead_genre_token_similarity(candidate: str, profile: str) -> float:
    """Return Jaccard token overlap for candidate/profile lead genres."""
    candidate_tokens = tokenize_genre(candidate)
    profile_tokens = tokenize_genre(profile)
    if not candidate_tokens or not profile_tokens:
        return 0.0
    union = candidate_tokens.union(profile_tokens)
    if not union:
        return 0.0
    return round(len(candidate_tokens.intersection(profile_tokens)) / len(union), 6)
