# Full Dataset Acquisition Checklist (MSD + Last.fm)

Date: 2026-03-21
Owner: Peach + AI
Status: planned (download not started)

## Goal
Acquire the full-scale MSD and full-scale Last.fm assets so BL-019 can be upgraded later from the 10K subset path to a large-corpus path.

## Storage and Time Pre-Check (Required)
- [ ] Confirm free disk space >= 650 GB on the target drive.
- [ ] Confirm stable internet for multi-hour transfer.
- [ ] Confirm where raw downloads will be staged (outside git repo if needed).

Rationale:
- Full MSD is large (official docs indicate about 280 GB download and about 493 GB mounted size in AWS snapshot form).
- Last.fm full train+test archives add significant extra space after extraction.

## Dataset A: Full Million Song Dataset (Required)

Official source pages:
- http://millionsongdataset.com/
- http://millionsongdataset.com/pages/getting-dataset/

Required for full MSD path:
- [ ] Full MSD core data (1,000,000 HDF5 track files) via official AWS snapshot path documented by MSD.
- [ ] Additional files bundle from MSD page (if not already present in your copy).
- [ ] Ensure `track_metadata.db` from AdditionalFiles is available and readable.

Notes:
- The official route for full data is the AWS public snapshot (documented by MSD as snapshot `snap-5178cf30`).
- If a trusted local/university copy is available, that is acceptable and usually faster than fresh internet download.

## Dataset B: Full Last.fm For MSD (Required)

Official source page:
- http://millionsongdataset.com/lastfm/

Required files:
- [ ] `lastfm_train.zip` (full train split)
  - http://labrosa.ee.columbia.edu/~dpwe/tmp/lastfm_train.zip
- [ ] `lastfm_test.zip` (full test split)
  - http://millionsongdataset.com/sites/default/files/lastfm/lastfm_test.zip

Optional but strongly recommended (for faster later ingestion):
- [ ] `lastfm_tags.db`
  - http://labrosa.ee.columbia.edu/~dpwe/tmp/lastfm_tags.db
- [ ] `lastfm_similars.db`
  - http://labrosa.ee.columbia.edu/~dpwe/tmp/lastfm_similars.db

Why both train and test:
- MSD docs state no data is removed by split; merging train+test gives full Last.fm coverage.

## Quick Validation After Download
- [ ] Verify each archive opens without corruption.
- [ ] Verify extracted JSON count is in expected large scale (not 10K subset size).
- [ ] Verify sampled JSON records contain keys: `track_id`, `artist`, `title`, `tags`, `similars`, `timestamp`.
- [ ] Verify MSD full data exposes large HDF5 tree and not only `millionsongsubset.tar.gz`.
- [ ] Record final file paths and file sizes in this document.

## Licensing and Use Notes
- MSD: research dataset, no audio payload (features + metadata only).
- Last.fm dataset page states research-only, non-commercial usage.

## Logging Requirements (Do Not Skip)
After each completed step, update:
- `00_admin/change_log.md` (new change record)
- `07_implementation/experiment_log.md` (run record with commands, metrics, output paths)
- `06_data_and_sources/dataset_registry.md` (source status and local path updates)

## Deferred Work (After Download)
- Build a full-scale BL-019 variant that reads full MSD instead of `millionsongsubset.tar.gz`.
- Replace subset Last.fm input (`lastfm_subset.zip`) with merged full train+test or SQLite-based ingestion.
- Re-baseline quality gates and expected row-count thresholds for full scale.
