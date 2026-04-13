"""Tests for alignment.aggregation — aggregate_matched_events."""
from alignment.aggregation import aggregate_matched_events


_DS001_DEFAULTS = {
    "ds001_spotify_id": "sp_default",
    "song": "Test Song",
    "artist": "Test Artist",
    "release": "2020",
    "duration_ms": "200000",
    "popularity": "50",
    "danceability": "0.5",
    "energy": "0.5",
    "key": "5",
    "mode": "1",
    "valence": "0.5",
    "tempo": "120",
    "genres": "pop",
    "tags": "",
    "lang": "en",
}


def _event(ds001_id, source_type="saved_tracks", interaction_type="history",
           spotify_track_id="sp1", preference_weight=1.0, interaction_count=5,
           match_method="metadata_fallback", **kwargs):
    event = dict(_DS001_DEFAULTS)
    event.update({
        "ds001_id": ds001_id,
        "source_type": source_type,
        "interaction_type": interaction_type,
        "spotify_track_id": spotify_track_id,
        "preference_weight": preference_weight,
        "interaction_count": interaction_count,
        "match_method": match_method,
    })
    event.update(kwargs)
    return event


class TestAggregateMatchedEvents:
    def test_empty_list_returns_empty_dict(self):
        assert aggregate_matched_events([]) == {}

    def test_single_event_correct_fields(self):
        events = [_event("ds1")]
        result = aggregate_matched_events(events)
        assert "ds1" in result
        agg = result["ds1"]
        assert agg["matched_event_count"] == 1
        assert agg["interaction_count_sum"] == 5
        assert agg["preference_weight_sum"] == 1.0
        assert agg["preference_weight_max"] == 1.0
        assert "saved_tracks" in agg["source_types"]
        assert "history" in agg["interaction_types"]
        assert "sp1" in agg["spotify_track_ids"]

    def test_two_events_same_id_accumulated(self):
        events = [
            _event("ds1", preference_weight=1.0, interaction_count=3),
            _event("ds1", source_type="top_tracks", preference_weight=2.0, interaction_count=7),
        ]
        result = aggregate_matched_events(events)
        agg = result["ds1"]
        assert agg["matched_event_count"] == 2
        assert agg["interaction_count_sum"] == 10
        assert agg["preference_weight_sum"] == 3.0
        assert agg["preference_weight_max"] == 2.0
        assert "saved_tracks" in agg["source_types"]
        assert "top_tracks" in agg["source_types"]

    def test_two_events_different_ids_separate_entries(self):
        events = [_event("ds1"), _event("ds2")]
        result = aggregate_matched_events(events)
        assert "ds1" in result
        assert "ds2" in result
        assert result["ds1"]["matched_event_count"] == 1
        assert result["ds2"]["matched_event_count"] == 1

    def test_source_types_is_set(self):
        events = [_event("ds1", source_type="saved_tracks"),
                  _event("ds1", source_type="top_tracks")]
        agg = aggregate_matched_events(events)["ds1"]
        assert isinstance(agg["source_types"], set)
        assert len(agg["source_types"]) == 2

    def test_interaction_types_union(self):
        # The aggregation splits "history,influence" by comma, so both "history"
        # and "influence" are individual members of the interaction_types set.
        events = [
            _event("ds1", interaction_type="history"),
            _event("ds1", interaction_type="history,influence"),
        ]
        agg = aggregate_matched_events(events)["ds1"]
        assert "history" in agg["interaction_types"]
        assert "influence" in agg["interaction_types"]

    def test_spotify_track_ids_set(self):
        events = [
            _event("ds1", spotify_track_id="sp1"),
            _event("ds1", spotify_track_id="sp2"),
        ]
        agg = aggregate_matched_events(events)["ds1"]
        assert "sp1" in agg["spotify_track_ids"]
        assert "sp2" in agg["spotify_track_ids"]

    def test_preference_weight_mode_max(self):
        events = [
            _event("ds1", preference_weight=1.0),
            _event("ds1", preference_weight=2.5),
        ]
        agg = aggregate_matched_events(
            events,
            aggregation_policy={"preference_weight_mode": "max", "preference_weight_cap_per_event": None},
        )["ds1"]
        assert agg["preference_weight_sum"] == 2.5
        assert agg["preference_weight_max"] == 2.5

    def test_preference_weight_mode_mean(self):
        events = [
            _event("ds1", preference_weight=1.0),
            _event("ds1", preference_weight=2.0),
            _event("ds1", preference_weight=3.0),
        ]
        agg = aggregate_matched_events(
            events,
            aggregation_policy={"preference_weight_mode": "mean", "preference_weight_cap_per_event": None},
        )["ds1"]
        assert agg["preference_weight_sum"] == 2.0

    def test_preference_weight_mode_capped(self):
        events = [
            _event("ds1", preference_weight=1.0),
            _event("ds1", preference_weight=2.0),
        ]
        agg = aggregate_matched_events(
            events,
            aggregation_policy={"preference_weight_mode": "capped", "preference_weight_cap_per_event": 1.2},
        )["ds1"]
        assert agg["preference_weight_sum"] == 2.2

    def test_confidence_defaults_to_one_for_exact_and_metadata_methods(self):
        events = [
            _event("ds1", match_method="spotify_id_exact", preference_weight=1.0),
            _event("ds1", match_method="metadata_fallback", preference_weight=2.0),
        ]
        agg = aggregate_matched_events(events)["ds1"]
        assert agg["match_confidence_score"] == 1.0

    def test_confidence_uses_fuzzy_combined_score_for_fuzzy_method(self):
        events = [
            _event(
                "ds1",
                match_method="fuzzy_title_artist",
                fuzzy_combined_score=0.42,
                preference_weight=1.0,
            )
        ]
        agg = aggregate_matched_events(events)["ds1"]
        assert agg["match_confidence_score"] == 0.42

    def test_confidence_weighted_mean_uses_preference_weight(self):
        events = [
            _event("ds1", match_method="spotify_id_exact", preference_weight=1.0),
            _event(
                "ds1",
                match_method="fuzzy_title_artist",
                fuzzy_combined_score=0.4,
                preference_weight=3.0,
            ),
        ]
        agg = aggregate_matched_events(events)["ds1"]
        assert agg["match_confidence_score"] == 0.55

    def test_confidence_fuzzy_missing_score_falls_back_to_one(self):
        events = [
            _event("ds1", match_method="fuzzy_title_artist", fuzzy_combined_score=None),
        ]
        agg = aggregate_matched_events(events)["ds1"]
        assert agg["match_confidence_score"] == 1.0
