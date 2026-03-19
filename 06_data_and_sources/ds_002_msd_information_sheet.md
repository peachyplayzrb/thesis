# Dataset Construction Information Sheet

## Deterministic Playlist Generation System (Thesis)

---

## 1. Purpose

The purpose of this dataset is to act as a candidate song database for a deterministic, content-based playlist generation system.

It must support:

- Transparent feature-based similarity
- Cross-source matching (Spotify -> dataset)
- Reproducible and observable recommendation behaviour

---

## 2. Selected Dataset Strategy

The dataset is constructed by integrating three established research datasets:

```
Million Song Dataset (MSD)
+ Last.fm Tag Dataset
+ MusicBrainz Mapping (via MSD)
```

This combination is widely used in academic recommender system research and provides complementary data types required for content-based recommendation.

---

## 3. Data Sources

### 3.1 Million Song Dataset (MSD)

Source: http://millionsongdataset.com/
Version Used: Subset (10,000 songs)

Purpose:
Provides core track-level features and metadata.

Key Variables:

- `track_id` (primary key)
- `artist_name`
- `title`
- `duration`
- `year`
- `tempo`
- `loudness`
- `key`
- `mode`

Role in System:

- Primary candidate song pool
- Source of audio-based similarity features

---

### 3.2 Last.fm Tag Dataset

Source: http://millionsongdataset.com/lastfm/

Purpose:
Provides user-generated semantic annotations (tags).

Key Variables:

- `track_id` (foreign key to MSD)
- `tag` (for example `rock`, `happy`, `electronic`)
- `weight` (importance of tag)

Role in System:

- Enables semantic similarity (genre, mood)
- Improves interpretability and explainability
- Supports user-understandable explanations

---

### 3.3 MusicBrainz Mapping (via MSD)

Source: MSD Additional Datasets

Purpose:
Links tracks to external identifiers (MusicBrainz IDs).

Key Variables:

- `track_id`
- `artist_name`
- `title`
- `mbid` (MusicBrainz ID)

Role in System:

- Supports cross-source alignment
- Enables future enrichment
- Assists in matching Spotify data to dataset

---

## 4. Final Dataset Structure

The integrated dataset contains the following fields:

```
track_id
artist_name
title
year
duration

tempo
loudness
key
mode

tags (aggregated list)

mbid (optional)
```

---

## 5. Data Integration Process

### Step 1 - Load MSD

- Extract track metadata and audio features from `.h5` files

### Step 2 - Join Last.fm Tags

- Match on `track_id`
- Aggregate tags per track

### Step 3 - Add MusicBrainz Mapping

- Join mapping file on `track_id`
- Attach MBID where available

### Step 4 - Clean and Normalize

- Normalize artist/title strings
- Handle missing values
- Aggregate tag weights

---

## 6. Spotify Integration

User data is obtained via Spotify API.

Available fields:

- `track name`
- `artist name`
- `ISRC` (when available)

Matching Strategy:

```
Primary: ISRC matching
Fallback: artist + title matching
```

Matching Outcomes:

- Exact match
- Fallback match
- Unmatched

All outcomes are logged for transparency.

---

## 7. Feature Categories

The dataset supports three feature types.

### 7.1 Audio Features

- `tempo`
- `loudness`
- `key`
- `mode`

### 7.2 Semantic Features

- `tags` (genre, mood, style)

### 7.3 Metadata

- `artist`
- `title`
- `year`

---

## 8. System Usage

The dataset is used to:

### 8.1 Build User Profile

- Aggregate features from the user's listening history

### 8.2 Match Input Songs

- Align user-selected songs to dataset entries

### 8.3 Generate Candidates

- Use full dataset as candidate pool

### 8.4 Rank Songs

- Apply deterministic similarity scoring

---

## 9. Limitations

- Not all Spotify tracks will match dataset entries
- Tag quality depends on user-generated data
- Audio features are limited compared to deep audio models
- No real-time catalogue updates

These limitations should be logged and reported explicitly if this path is implemented later.

---

## 10. Justification

This dataset design is chosen because it:

- Supports transparent feature-based recommendation
- Enables deterministic and reproducible outputs
- Uses widely accepted research datasets
- Avoids unnecessary system complexity
- Fits within BSc project constraints

---

## 11. Design Alignment With Thesis

| Objective | Support |
| --- | --- |
| Transparency | Explicit features and tags |
| Controllability | Feature weighting and scoring |
| Observability | Track-level and score-level logging |
| Reproducibility | Deterministic dataset + pipeline |

---

## 12. Summary

The dataset provides a structured, multi-source, and research-backed foundation for building a deterministic playlist generation system. It balances practicality, academic validity, and system transparency, making it a viable fallback or future extension path if the thesis later reopens corpus engineering.