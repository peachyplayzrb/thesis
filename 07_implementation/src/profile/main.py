from __future__ import annotations

from profile.stage import NUMERIC_FEATURE_COLUMNS, SUMMARY_FEATURE_COLUMNS, ProfileStage


def infer_user_id_from_ingestion() -> str | None:
    return ProfileStage().infer_user_id_from_ingestion()


def resolve_bl004_runtime_controls() -> dict[str, object]:
    return ProfileStage().resolve_runtime_controls().as_mapping()


def resolve_lead_genre(genres: list[str], tags: list[str]) -> str:
    return ProfileStage.resolve_lead_genre(genres, tags)


def sorted_weight_map(weight_map: dict[str, float], limit: int) -> list[dict[str, float | str]]:
    return ProfileStage.sorted_weight_map(weight_map, limit)


def circular_mean_key(sum_x: float, sum_y: float) -> float | None:
    return ProfileStage.circular_mean_key(sum_x, sum_y)


def main() -> None:
    ProfileStage().run()


if __name__ == "__main__":
    main()
