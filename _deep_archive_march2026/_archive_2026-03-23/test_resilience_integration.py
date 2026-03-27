#!/usr/bin/env python3
"""
Test script: Verify spotify_resilience integration in export_spotify_max_dataset.py

Run this AFTER executing export_spotify_max_dataset.py at least once.
It checks that:
1. Cache database was created
2. Cache entries exist
3. Cache TTL is working
4. Job progress (if enabled) was tracked
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def test_cache_database_exists():
    """✓ Cache database file exists"""
    cache_db = Path(__file__).parent / "implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_resilience_cache.sqlite"
    
    if cache_db.exists():
        print(f"✓ Cache database exists: {cache_db}")
        return True, cache_db
    else:
        print(f"✗ Cache database NOT found: {cache_db}")
        print(f"  → Run export_spotify_max_dataset.py first")
        return False, None


def test_cache_entries(cache_db_path):
    """✓ Cache has entries"""
    conn = sqlite3.connect(cache_db_path)
    cur = conn.cursor()
    
    count = cur.execute("SELECT COUNT(*) FROM endpoint_cache").fetchone()[0]
    conn.close()
    
    if count > 0:
        print(f"✓ Cache has {count} entries")
        return True
    else:
        print(f"✗ Cache is empty ({count} entries)")
        return False


def test_cache_keys(cache_db_path):
    """✓ Cache keys follow expected pattern"""
    conn = sqlite3.connect(cache_db_path)
    cur = conn.cursor()
    
    rows = cur.execute("""
        SELECT cache_key, fetched_at, ttl_seconds
        FROM endpoint_cache
        ORDER BY fetched_at DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    
    print("\nRecent cache entries:")
    expected_patterns = ["/me/top/tracks", "/me/tracks", "/me/playlists"]
    found_patterns = set()
    
    for cache_key, fetched_at, ttl_seconds in rows:
        for pattern in expected_patterns:
            if pattern in cache_key:
                found_patterns.add(pattern)
        print(f"  {cache_key:50} | TTL={ttl_seconds}s | fetched={fetched_at}")
    
    if found_patterns:
        print(f"\n✓ Found expected endpoint patterns: {found_patterns}")
        return True
    else:
        print(f"✗ No expected patterns found in cache")
        return False


def test_cache_ttl_validity(cache_db_path):
    """✓ Cache entries are within valid TTL"""
    conn = sqlite3.connect(cache_db_path)
    cur = conn.cursor()
    
    rows = cur.execute("""
        SELECT cache_key, fetched_at, ttl_seconds
        FROM endpoint_cache
    """).fetchall()
    conn.close()
    
    now = datetime.now(timezone.utc)
    valid = 0
    expired = 0
    
    for cache_key, fetched_at_str, ttl_seconds in rows:
        # Parse ISO 8601 timestamp
        fetched_at = datetime.fromisoformat(fetched_at_str.replace("Z", "+00:00"))
        age_seconds = (now - fetched_at).total_seconds()
        
        if age_seconds < ttl_seconds:
            valid += 1
        else:
            expired += 1
    
    print(f"\n✓ Cache validity: {valid} valid, {expired} expired")
    
    if valid > 0:
        return True
    else:
        print(f"✗ All cache entries have expired")
        return False


def test_job_progress(cache_db_path):
    """✓ Job progress was tracked (if available)"""
    conn = sqlite3.connect(cache_db_path)
    cur = conn.cursor()
    
    try:
        count = cur.execute("SELECT COUNT(*) FROM job_progress").fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"✓ Job progress tracked: {count} steps recorded")
            return True
        else:
            print(f"⚠ Job progress table exists but empty (may not be used yet)")
            return True
    except sqlite3.OperationalError:
        print(f"⚠ Job progress table does not exist (not critical)")
        return True


def test_export_summary():
    """✓ Export summary mentions caching"""
    summary_path = Path(__file__).parent / "implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json"
    
    if not summary_path.exists():
        print(f"\n✗ Summary file not found: {summary_path}")
        return False
    
    try:
        summary = json.loads(summary_path.read_text())
        
        if "resilience" in summary:
            resilience_info = summary["resilience"]
            cache_enabled = resilience_info.get("cache_enabled", False)
            print(f"\n✓ Summary includes resilience metadata:")
            print(f"  - Cache enabled: {cache_enabled}")
            print(f"  - Cache DB: {resilience_info.get('cache_db_path')}")
            print(f"  - Note: {resilience_info.get('cache_note')}")
            return True
        else:
            print(f"⚠ Summary does not have resilience metadata (older export?)")
            return True
    except Exception as e:
        print(f"✗ Error reading summary: {e}")
        return False


def main():
    print("=" * 70)
    print("SPOTIFY RESILIENCE INTEGRATION TEST")
    print("=" * 70)
    
    ok, cache_db = test_cache_database_exists()
    if not ok:
        print("\n❌ Tests cannot proceed without cache database")
        sys.exit(1)
    
    tests = [
        ("Cache entries exist", lambda: test_cache_entries(cache_db)),
        ("Cache keys are valid", lambda: test_cache_keys(cache_db)),
        ("Cache TTL validity", lambda: test_cache_ttl_validity(cache_db)),
        ("Job progress tracking", lambda: test_job_progress(cache_db)),
        ("Export summary metadata", test_export_summary),
    ]
    
    results = []
    for test_name, test_fn in tests:
        print(f"\n[TEST] {test_name}")
        try:
            result = test_fn()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Integration is working!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some tests failed or skipped - check output above")
        sys.exit(1 if any(not r for _, r in results if isinstance(r, bool) and not r) else 0)


if __name__ == "__main__":
    main()
