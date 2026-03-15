import csv
import re
import argparse
import unicodedata
from pathlib import Path
from collections import defaultdict
from multiprocessing import get_context
from pypdf import PdfReader
from rapidfuzz import fuzz

ROOT = Path(r"c:\Users\Timothy\Desktop\thesis-main\thesis-main")
CHAPTER = ROOT / "08_writing" / "chapter2.md"
INDEX = ROOT / "03_literature" / "source_index.csv"
REF_BIB = ROOT / "08_writing" / "references.bib"
OUT_MD = ROOT / "09_quality_control" / "chapter2_verbatim_audit.md"

PDF_DIRS = [
    ROOT / "10_resources" / "papers",
    ROOT / "10_resources" / "previous_drafts" / "lit_review_resource_pack" / "files",
]


def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fold_ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def norm_name_token(s: str) -> str:
    s = fold_ascii(s).lower()
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


def tokenize(s: str):
    return [t for t in normalize(s).split() if len(t) > 2]


def split_sentences(text: str):
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for p in parts:
        p = p.strip()
        if 35 <= len(p) <= 500:
            out.append(p)
    return out


def first_author_surname(authors_field: str) -> str:
    if not authors_field:
        return ""
    first = authors_field.split(";")[0].strip()
    # Handles either "Surname" or "Surname, Given" style.
    first = first.split(",")[0].strip()
    return norm_name_token(first)


def build_author_year_key_map(index_rows):
    out = defaultdict(list)
    for r in index_rows:
        key = r.get("citation_key", "").strip()
        if not key:
            continue
        year = str(r.get("year", "")).strip()
        surname = first_author_surname(r.get("authors", ""))
        if not year or not surname:
            continue
        out[(surname, year)].append(key)
    return out


def extract_author_year_keys(sentence: str, author_year_key_map):
    keys = set()

    for group in re.findall(r"\(([^()]{3,260})\)", sentence):
        if not re.search(r"\b\d{4}\b", group):
            continue
        for chunk in group.split(";"):
            m = re.search(
                r"([A-Za-zÀ-ÖØ-öø-ÿ'`.-]+)(?:\s+et\s+al\.)?(?:\s+and\s+[A-Za-zÀ-ÖØ-öø-ÿ'`.-]+)?\s*,\s*(\d{4})",
                chunk,
                re.IGNORECASE,
            )
            if not m:
                continue
            surname = norm_name_token(m.group(1))
            year = m.group(2)
            for k in author_year_key_map.get((surname, year), []):
                keys.add(k)

    return sorted(keys)


def extract_claim_units(md_text: str, author_year_key_map):
    # Capture sentence-level claim units around citation groups [@k1; @k2]
    # and author-year patterns (Surname et al., YYYY; Surname and Surname, YYYY).
    lines = md_text.splitlines()
    blocks = []
    buf = []
    for line in lines:
        if line.strip() == "":
            if buf:
                blocks.append(" ".join(buf).strip())
                buf = []
        else:
            if not line.strip().startswith("#"):
                buf.append(line.strip())
    if buf:
        blocks.append(" ".join(buf).strip())

    claims = []
    cite_pat = re.compile(r"\[@([^\]]+)\]")
    for block in blocks:
        # split into sentences for finer matching
        for sent in split_sentences(block):
            cites = cite_pat.findall(sent)
            keys = []
            if cites:
                for group in cites:
                    for item in group.split(";"):
                        k = item.strip().lstrip("@")
                        if k:
                            keys.append(k)
            else:
                keys.extend(extract_author_year_keys(sent, author_year_key_map))

            if not keys:
                continue
            clean_sent = cite_pat.sub("", sent).strip()
            clean_sent = re.sub(r"\s+", " ", clean_sent)
            if clean_sent:
                claims.append((clean_sent, sorted(set(keys))))
    return claims


def load_index(path: Path):
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def load_bib_attachment_map(path: Path):
    """Map citation keys to attached PDF basenames from references.bib file fields."""
    if not path.exists():
        return {}

    text = path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.split(r"\n@", text)
    out = {}

    for i, raw_block in enumerate(blocks):
        block = raw_block if i == 0 else "@" + raw_block
        m_key = re.search(r"@\w+\{\s*([^,\s]+)\s*,", block)
        if not m_key:
            continue
        key = m_key.group(1).strip()

        m_file = re.search(r"\bfile\s*=\s*\{([^}]*)\}", block, re.IGNORECASE | re.DOTALL)
        if not m_file:
            continue
        file_field = m_file.group(1)
        m_pdf = re.search(r"PDF:[^:]*?/([^/:]+?\.pdf):", file_field, re.IGNORECASE)
        if not m_pdf:
            continue
        out[key] = m_pdf.group(1).strip()

    return out


def find_all_pdfs():
    pdfs = []
    for d in PDF_DIRS:
        if d.exists():
            pdfs.extend(d.rglob("*.pdf"))
    return pdfs


def score_pdf_match(row, pdf_path: Path):
    stem = normalize(pdf_path.stem)
    title = normalize(row.get("title", ""))
    authors = normalize(row.get("authors", ""))
    year = str(row.get("year", "")).strip()
    key = normalize(row.get("citation_key", ""))

    score = 0
    if year and year in stem:
        score += 20

    title_tokens = set(tokenize(title))
    stem_tokens = set(tokenize(stem))
    if title_tokens:
        overlap = len(title_tokens & stem_tokens) / max(1, len(title_tokens))
        score += int(overlap * 60)

    # first author token boost
    first_author = authors.split(";")[0].strip().split(" ")[0] if authors else ""
    if first_author and first_author in stem:
        score += 15

    # key token boost
    key_tokens = set(tokenize(key))
    if key_tokens:
        score += int(10 * (len(key_tokens & stem_tokens) / max(1, len(key_tokens))))

    return score


def map_keys_to_pdfs(index_rows, pdfs):
    bib_attachment_map = load_bib_attachment_map(REF_BIB)

    pdf_by_norm_stem = defaultdict(list)
    for p in pdfs:
        pdf_by_norm_stem[normalize(p.stem)].append(p)

    def choose_preferred_pdf(candidates):
        if not candidates:
            return None
        return sorted(candidates, key=lambda p: ("10_resources\\papers" not in str(p), len(str(p))))[0]

    mapping = {}
    for row in index_rows:
        key = row["citation_key"]

        # 1) Preferred: direct BibTeX attachment filename match by normalized stem.
        bib_filename = bib_attachment_map.get(key)
        if bib_filename:
            bib_norm_stem = normalize(Path(bib_filename).stem)
            candidates = pdf_by_norm_stem.get(bib_norm_stem, [])
            chosen = choose_preferred_pdf(candidates)
            if chosen:
                mapping[key] = {
                    "pdf": chosen,
                    "score": 1000,
                    "method": "bib_attachment_exact_stem",
                }
                continue

            # If exact normalized stem fails (e.g., punctuation/encoding drift),
            # use high-threshold fuzzy stem matching as a robust fallback.
            stem_ranked = sorted(
                (
                    (fuzz.token_set_ratio(bib_norm_stem, normalize(p.stem)), p)
                    for p in pdfs
                ),
                key=lambda x: x[0],
                reverse=True,
            )
            top_stem_score, top_stem_pdf = stem_ranked[0] if stem_ranked else (0, None)
            if top_stem_pdf and top_stem_score >= 90:
                mapping[key] = {
                    "pdf": top_stem_pdf,
                    "score": top_stem_score,
                    "method": "bib_attachment_fuzzy_stem",
                }
                continue

        # 2) Fallback: fuzzy metadata-based filename matching with confidence floor.
        ranked = sorted(
            ((score_pdf_match(row, p), p) for p in pdfs),
            key=lambda x: x[0],
            reverse=True,
        )
        best_score, best_pdf = ranked[0] if ranked else (0, None)
        if best_score < 50:
            best_pdf = None
        mapping[key] = {
            "pdf": best_pdf,
            "score": best_score,
            "method": "fuzzy_title_author_year" if best_pdf else "no_confident_match",
        }
    return mapping


def _extract_pdf_text_worker(pdf_path_str: str, max_pages: int):
    pdf_path = Path(pdf_path_str)
    try:
        reader = PdfReader(str(pdf_path))
        pages = reader.pages[:max_pages]
        txt = []
        for pg in pages:
            try:
                # Some scanned/complex pages can fail or stall extraction; skip safely.
                t = pg.extract_text() or ""
            except BaseException:
                continue
            if t:
                txt.append(t)
        return "\n".join(txt)
    except Exception:
        return ""


def extract_pdf_text(pdf_path: Path, max_pages: int = 12, timeout_sec: int = 20):
    # Isolate each PDF extraction in a subprocess so malformed PDFs cannot hang the whole audit.
    try:
        ctx = get_context("spawn")
        with ctx.Pool(processes=1) as pool:
            res = pool.apply_async(_extract_pdf_text_worker, (str(pdf_path), max_pages))
            try:
                return res.get(timeout=timeout_sec)
            except Exception:
                pool.terminate()
                return ""
    except Exception:
        return ""


def best_quote_matches(claim_sentence, doc_sentences, top_k=2):
    scored = []
    for s in doc_sentences:
        score = fuzz.token_set_ratio(claim_sentence, s)
        if score >= 35:
            scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


def status_from_score(score):
    if score >= 65:
        return "supported"
    if score >= 50:
        return "partially_supported"
    return "weak_support"


def parse_args():
    parser = argparse.ArgumentParser(description="Run sentence-level claim audit for Chapter 2 markdown.")
    parser.add_argument("--chapter", type=str, default=str(CHAPTER), help="Path to chapter markdown file")
    parser.add_argument("--out", type=str, default=str(OUT_MD), help="Path to output audit markdown file")
    return parser.parse_args()


def main():
    args = parse_args()
    chapter_path = Path(args.chapter)
    out_path = Path(args.out)

    md_text = chapter_path.read_text(encoding="utf-8")
    index_rows = load_index(INDEX)
    author_year_key_map = build_author_year_key_map(index_rows)
    claims = extract_claim_units(md_text, author_year_key_map)
    index_by_key = {r["citation_key"]: r for r in index_rows}
    pdfs = find_all_pdfs()
    key_to_pdf = map_keys_to_pdfs(index_rows, pdfs)

    claims_by_key = defaultdict(list)
    for sent, keys in claims:
        for k in keys:
            claims_by_key[k].append(sent)

    # only keys cited in chapter
    cited_keys = sorted(claims_by_key.keys())

    # extract each cited doc once
    doc_sentence_cache = {}
    for k in cited_keys:
        map_entry = key_to_pdf.get(k, {"pdf": None, "score": 0, "method": "missing_key"})
        pdf = map_entry["pdf"]
        if not pdf:
            doc_sentence_cache[k] = []
            continue
        text = extract_pdf_text(pdf)
        doc_sentence_cache[k] = split_sentences(text)

    lines = []
    lines.append("# Chapter 2 Verbatim Claim Audit")
    lines.append("")
    lines.append(f"Scope: sentence-level claim checks in `{chapter_path}` against extracted text from mapped local PDFs.")
    lines.append("Method note: automated lexical matching (RapidFuzz token-set ratio) with manual thresholding.")
    if not claims:
        lines.append("Parser note: 0 claim units were detected after citation parsing for key-based and author-year styles; manual spot checks are required.")
    lines.append("")

    summary = {"supported": 0, "partially_supported": 0, "weak_support": 0, "no_match": 0}

    for k in cited_keys:
        row = index_by_key.get(k)
        title = row.get("title", "UNKNOWN") if row else "UNKNOWN"
        map_entry = key_to_pdf.get(k, {"pdf": None, "score": 0, "method": "missing_key"})
        pdf = map_entry["pdf"]
        map_score = map_entry["score"]
        map_method = map_entry["method"]
        lines.append(f"## {k}")
        lines.append(f"- title: {title}")
        lines.append(f"- mapped_pdf: {pdf if pdf else 'NOT_FOUND'}")
        lines.append(f"- mapping_score: {map_score}")
        lines.append(f"- mapping_method: {map_method}")

        key_claims = claims_by_key[k]
        doc_sents = doc_sentence_cache.get(k, [])

        if not doc_sents:
            lines.append("- result: no extractable text for this source")
            lines.append("")
            continue

        lines.append("- claim_checks:")
        for i, c in enumerate(key_claims, start=1):
            matches = best_quote_matches(c, doc_sents, top_k=2)
            if not matches:
                status = "no_match"
                summary[status] += 1
                lines.append(f"  - claim_{i}_status: {status}")
                lines.append(f"    claim: \"{c}\"")
                continue

            top_score, top_quote = matches[0]
            status = status_from_score(top_score)
            summary[status] += 1
            lines.append(f"  - claim_{i}_status: {status}")
            lines.append(f"    score: {top_score}")
            lines.append(f"    claim: \"{c}\"")
            lines.append(f"    quote_candidate: \"{top_quote}\"")
            if len(matches) > 1:
                lines.append(f"    secondary_score: {matches[1][0]}")
                lines.append(f"    secondary_quote: \"{matches[1][1]}\"")

        lines.append("")

    lines.append("## Summary")
    total = sum(summary.values())
    lines.append(f"- total_claim_checks: {total}")
    for k in ["supported", "partially_supported", "weak_support", "no_match"]:
        lines.append(f"- {k}: {summary[k]}")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE: {out_path}")


if __name__ == "__main__":
    main()
