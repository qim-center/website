#!/usr/bin/env python3
"""Update data/publications.json from the ORCID public API.

Authors are discovered from the ORCID links in data/about/members/*.yaml.
Existing entries are never overwritten: only a missing DOI is filled in, and
hand-curated ``keywords`` / ``note`` are preserved. New entries are added with
empty ``keywords`` so that they can be tagged by hand.

Usage:
    python scripts/update_publications.py                # dry run (prints summary)
    python scripts/update_publications.py --write        # apply changes
    python scripts/update_publications.py --since 2015   # override the default cutoff year (2018); 0 = no cutoff
    python scripts/update_publications.py --filter       # drop new works unrelated to QIM (LLM)

Only the Python standard library is used.

Note: ORCID work records often lack full author lists. Authors are taken from
the record's BibTeX citation or contributor list when present; otherwise the
ORCID owner's name is used and the entry is flagged in the output so the
author list can be completed by hand.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMBERS_DIR = ROOT / "data" / "about" / "members"
PUBS_FILE = ROOT / "data" / "publications.json"
EXTRA_FILE = ROOT / "data" / "publications-extra.json"
API = "https://pub.orcid.org/v3.0"
USER_AGENT = "qim-website-publications/1.0 (https://qim.dk)"
KEY_ORDER = [
    "authors", "year", "title", "journal", "booktitle", "volume", "issue",
    "pages", "publisher", "address", "note", "doi", "url", "keywords",
]
WANTED_TYPES = {"journal-article", "conference-paper", "book-chapter"}
DEFAULT_SINCE = 2018  # default cutoff year for new works
CONFERENCE_TYPES = {"conference-paper"}
ORCID_RE = re.compile(r"orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])", re.I)
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.I)


# ---------- helpers ----------
def norm_title(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"<[^>]*>", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def extract_doi(s: str | None) -> str | None:
    m = DOI_RE.search(s or "")
    return re.sub(r"[.,;)]+$", "", m.group(0)).lower() if m else None


def strip_tags(s: str | None) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", "", s or "")).strip()


def format_author(name: str) -> str:
    """'Hans Martin Kjer' or 'Kjer, Hans Martin' -> 'Kjer, H.M.' (existing data format)."""
    name = strip_tags(name)
    if "," in name:
        surname, given = [p.strip() for p in name.split(",", 1)]
    else:
        parts = name.replace(".", " ").split()
        if len(parts) < 2:
            return name
        surname, given = parts[-1], " ".join(parts[:-1])
    initials = "".join(p[0].upper() + "." for p in re.split(r"[\s.\-]+", given) if p)
    return f"{surname}, {initials}" if initials else surname


def member_orcids() -> tuple[list[str], list[str]]:
    # Regex-based on purpose: some member files contain multi-line strings that
    # strict YAML parsers reject (Hugo accepts them), and only the link is needed.
    orcids: list[str] = []
    missing: list[str] = []
    for f in sorted(MEMBERS_DIR.glob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        found = [m.upper() for m in ORCID_RE.findall(text)]
        if found:
            orcids += [o for o in found if o not in orcids]
        else:
            m = re.search(r'^name:\s*"?([^"\n]+)"?', text, re.M)
            missing.append(m.group(1) if m else f.stem)
    return orcids, missing


def get_json(url: str, tries: int = 3) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError):
            if attempt == tries:
                raise
            time.sleep(attempt)
    raise RuntimeError("unreachable")


def val(d: dict | None, *path: str) -> str | None:
    for p in path:
        d = d.get(p) if isinstance(d, dict) else None
    return d if isinstance(d, str) else None


def doi_of(external_ids: dict | None) -> str | None:
    for e in (external_ids or {}).get("external-id", []) or []:
        if (e.get("external-id-type") or "").lower() == "doi":
            return extract_doi(e.get("external-id-value"))
    return None


def parse_bibtex(text: str) -> dict[str, str]:
    """Very small BibTeX field parser (handles `{...}` and `"..."` values)."""
    fields: dict[str, str] = {}
    for m in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|\d+)", text):
        v = m.group(2)
        if v[0] in "{\"":
            v = v[1:-1]
        fields[m.group(1).lower()] = re.sub(r"[{}]", "", v).strip()
    return fields


def fetch_summaries(orcid: str) -> list[dict]:
    """Return one preferred work summary per group (ORCID already de-duplicates)."""
    data = get_json(f"{API}/{orcid}/works")
    out = []
    for g in data.get("group", []):
        sums = g.get("work-summary") or []
        if sums:
            s = sums[0]
            s["_doi"] = doi_of(g.get("external-ids")) or doi_of(s.get("external-ids"))
            out.append(s)
    return out


def fetch_details(orcid: str, put_codes: list[int]) -> list[dict]:
    works = []
    for i in range(0, len(put_codes), 100):
        codes = ",".join(map(str, put_codes[i:i + 100]))
        data = get_json(f"{API}/{orcid}/works/{codes}")
        works += [b["work"] for b in data.get("bulk", []) if b.get("work")]
    return works


def to_entry(work: dict, doi: str | None, owner: str) -> tuple[dict, bool]:
    """Convert an ORCID work to our schema. Returns (entry, authors_complete)."""
    year = val(work, "publication-date", "year", "value")
    e: dict = {"year": year, "title": strip_tags(val(work, "title", "title", "value"))}

    bib: dict[str, str] = {}
    cit = work.get("citation") or {}
    if (cit.get("citation-type") or "").lower() == "bibtex" and cit.get("citation-value"):
        bib = parse_bibtex(cit["citation-value"])

    names = [
        c["credit-name"]["value"]
        for c in (work.get("contributors") or {}).get("contributor", []) or []
        if (c.get("credit-name") or {}).get("value")
    ]
    if bib.get("author"):
        names = [n.strip() for n in re.split(r"\s+and\s+", bib["author"]) if n.strip()]
    complete = bool(names)
    e["authors"] = " and ".join(format_author(n) for n in names) if names else format_author(owner)

    venue = strip_tags(val(work, "journal-title", "value") or bib.get("journal") or bib.get("booktitle") or "")
    wtype = (work.get("type") or "").lower().replace("_", "-")
    if venue:
        e["booktitle" if wtype in CONFERENCE_TYPES else "journal"] = venue
    if bib.get("volume"):
        e["volume"] = bib["volume"]
    if bib.get("number"):
        e["issue"] = bib["number"]
    if bib.get("pages"):
        e["pages"] = re.sub(r"\s*[-\u2013\u2014]+\s*", "-", bib["pages"])
    if bib.get("publisher"):
        e["publisher"] = bib["publisher"]
    if doi:
        e["doi"] = doi
        e["url"] = f"https://doi.org/{doi}"
    elif val(work, "url", "value"):
        e["url"] = work["url"]["value"]
    e["keywords"] = []
    return e, complete


def ordered(e: dict) -> dict:
    out = {k: e[k] for k in KEY_ORDER if k in e}
    out.update({k: v for k, v in e.items() if k not in out})
    return out


# ---------- LLM relevance filter (DTU CampusAI, OpenAI-compatible) ----------
CAMPUSAI_URL = "https://api.campusai.compute.dtu.dk/v1/chat/completions"
CAMPUSAI_MODEL = "cai-instant"
MAX_WORKERS = 4  # the key allows 8 concurrent requests; never use more than half
DEFAULT_WORKERS = 2
SCOPE_PROMPT = """You decide whether a scientific publication is relevant to the work of the QIM Center \
(DTU Compute / MAX IV / Lund University). QIM works on quantitative imaging and large-scale 3D image \
analysis: X-ray, neutron and electron tomography (e.g. uCT, synchrotron imaging), tomographic \
reconstruction, image analysis, computer vision, machine learning / deep learning for images and \
segmentation, multimodal imaging, materials characterization with imaging, beamline/instrument \
descriptions for imaging, and research software, data management and open-source tools for imaging.

A paper is relevant if imaging or image/volume data analysis is a substantial part of its methods or \
contribution, including applications (materials, biology, medicine) where such imaging or analysis is \
used. It is NOT relevant if it is unrelated to imaging or computational image analysis (for example \
pure clinical, genetic, chemical or astronomy work without such a component), or if it only mentions \
imaging in passing.

Answer ONLY with a JSON object: {"relevant": true|false, "reason": "<max 15 words>"}"""


def classify(entry: dict, api_key: str) -> tuple[bool | None, str]:
    """Ask CampusAI whether an entry is relevant. Returns (relevant, reason); relevant is None on failure."""
    venue = entry.get("journal") or entry.get("booktitle") or "unknown venue"
    user = f"Title: {entry['title']}\nVenue: {venue}\nYear: {entry['year']}\nAuthors: {entry['authors']}"
    body = json.dumps({
        "model": CAMPUSAI_MODEL,
        "reasoning_effort": "none",  # plain classification; avoids reasoning tokens eating max_tokens
        "temperature": 0,
        "max_tokens": 120,
        "messages": [{"role": "system", "content": SCOPE_PROMPT}, {"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(
        CAMPUSAI_URL,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "User-Agent": USER_AGENT},
    )
    last = ""
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                content = json.load(r)["choices"][0]["message"]["content"] or ""
            m = re.search(r"\{.*\}", content, re.S)
            parsed = json.loads(m.group(0)) if m else {}
            if isinstance(parsed.get("relevant"), bool):
                return parsed["relevant"], str(parsed.get("reason", "")).strip()
            last = f"unparseable answer: {content[:80]!r}"
        except urllib.error.HTTPError as ex:
            err_body = ""
            try:
                err_body = ex.read().decode("utf-8", errors="replace")[:120].strip()
            except Exception:
                pass
            last = f"HTTP {ex.code}" + (f": {err_body}" if err_body else "")
            if ex.code in (400, 401, 403, 404, 422):  # client error: retrying will not help
                return None, last
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as ex:
            last = str(ex)
        print(f"\n  ! LLM retry {attempt}/5 ({last})", file=sys.stderr, flush=True)
        time.sleep(2 * attempt)  # also covers 429 (concurrency limit)
    return None, last


def filter_entries(candidates: list[tuple[dict, bool]], api_key: str, workers: int):
    """Classify candidates with a small thread pool. Returns (kept, rejected, unclassified)."""
    kept, rejected, unclassified = [], [], []
    n = len(candidates)
    results: list[tuple[bool | None, str]] = [(None, "")] * n
    done = n_kept = n_rejected = n_err = 0
    print(f"  Classifying: [0/{n}]   0% (0 kept, 0 rejected)", end="", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        fut_to_idx = {pool.submit(classify, c[0], api_key): i for i, c in enumerate(candidates)}
        for fut in concurrent.futures.as_completed(fut_to_idx):
            i = fut_to_idx[fut]
            rel, reason = fut.result()
            results[i] = (rel, reason)
            done += 1
            if rel is True:
                n_kept += 1
            elif rel is False:
                n_rejected += 1
            else:
                n_err += 1
            pct = done * 100 // n
            err_str = f", {n_err} errors" if n_err else ""
            print(
                f"\r  Classifying: [{done}/{n}] {pct:3d}% ({n_kept} kept, {n_rejected} rejected{err_str})",
                end="",
                flush=True,
            )
    print()
    for cand, (relevant, reason) in zip(candidates, results):
        if relevant is None:
            unclassified.append((cand, reason))  # kept: never silently drop on an error
        elif relevant:
            kept.append(cand)
        else:
            rejected.append((cand, reason))
    return kept, rejected, unclassified


# ---------- main ----------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="apply changes to data/publications.json")
    ap.add_argument("--since", type=int, default=DEFAULT_SINCE,
                    help=f"only include works from this year onwards (default {DEFAULT_SINCE}; 0 = no cutoff)")
    ap.add_argument("--filter", action="store_true",
                    help="drop new works unrelated to QIM using DTU CampusAI (needs CAMPUSAI_API_KEY)")
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                    help=f"parallel LLM requests (default {DEFAULT_WORKERS}, max {MAX_WORKERS})")
    args = ap.parse_args()
    if not 1 <= args.workers <= MAX_WORKERS:
        ap.error(f"--workers must be between 1 and {MAX_WORKERS}")
    api_key = os.environ.get("CAMPUSAI_API_KEY", "")
    if args.filter and not api_key:
        ap.error("--filter needs the CAMPUSAI_API_KEY environment variable (see README / script docstring)")

    orcids, missing = member_orcids()
    print(f"Members with ORCID: {len(orcids)}")
    if missing:
        print(f"Members without an ORCID (skipped): {', '.join(missing)}")

    existing = json.loads(PUBS_FILE.read_text(encoding="utf-8"))
    by_doi: dict[str, int] = {}
    by_title: dict[str, int] = {}
    for i, e in enumerate(existing):
        d = extract_doi(e.get("doi") or e.get("url"))
        if d:
            by_doi[d] = i
        by_title[f"{norm_title(e.get('title', ''))}|{e.get('year')}"] = i

    result = [dict(e) for e in existing]
    candidates: list[tuple[dict, bool]] = []  # new entries, before the optional relevance filter
    updated: list[str] = []
    seen: set[str] = set()  # de-duplicate works shared between several members (or already in publications-extra.json)
    if EXTRA_FILE.exists():
        for e in json.loads(EXTRA_FILE.read_text(encoding="utf-8")):
            d = extract_doi(e.get("doi") or e.get("url"))
            if d:
                seen.add(f"doi:{d}")
            seen.add(f"t:{norm_title(e.get('title', ''))}|{e.get('year')}")
    total = 0

    n_orcids = len(orcids)
    for m_idx, orcid in enumerate(orcids, 1):
        pct = m_idx * 100 // n_orcids if n_orcids else 100
        print(f"\rFetching ORCID works: [{m_idx}/{n_orcids}] {pct:3d}% ({orcid})", end="", flush=True)
        try:
            summaries = fetch_summaries(orcid)
        except urllib.error.URLError as ex:
            print(f"\n  ! {orcid}: {ex}", file=sys.stderr)
            continue
        owner_name = ""
        todo: list[tuple[dict, str | None]] = []
        for s in summaries:
            wtype = (s.get("type") or "").lower().replace("_", "-")
            year = val(s, "publication-date", "year", "value")
            title = strip_tags(val(s, "title", "title", "value"))
            if wtype not in WANTED_TYPES or not year or not title:
                continue
            if args.since and int(year) < args.since:
                continue
            total += 1
            doi = s["_doi"]
            key = f"doi:{doi}" if doi else f"t:{norm_title(title)}|{year}"
            if key in seen:
                continue
            seen.add(key)

            idx = by_doi.get(doi) if doi else None
            if idx is None:
                idx = by_title.get(f"{norm_title(title)}|{year}")
            if idx is not None:
                if doi and not result[idx].get("doi"):
                    result[idx]["doi"] = doi
                    updated.append(f"{result[idx]['title']} (+doi)")
                continue
            todo.append((s, doi))

        if not todo:
            continue
        # Owner name (fallback author) from the record itself.
        try:
            person = get_json(f"{API}/{orcid}/person")
            n = person.get("name") or {}
            owner_name = f"{val(n, 'given-names', 'value') or ''} {val(n, 'family-name', 'value') or ''}".strip()
        except urllib.error.URLError:
            owner_name = orcid
        details = {w["put-code"]: w for w in fetch_details(orcid, [s["put-code"] for s, _ in todo])}
        for s, doi in todo:
            w = details.get(s["put-code"], s)
            entry, complete = to_entry(w, doi, owner_name)
            entry["year"] = entry["year"] or val(s, "publication-date", "year", "value")
            candidates.append((entry, complete))
    if n_orcids:
        print()

    rejected: list[tuple[tuple[dict, bool], str]] = []
    unclassified: list[tuple[tuple[dict, bool], str]] = []
    if args.filter and candidates:
        print(f"\nClassifying {len(candidates)} new works with {CAMPUSAI_MODEL} ({args.workers} parallel requests)...")
        added, rejected, unclassified = filter_entries(candidates, api_key, args.workers)
        added += [c for c, _ in unclassified]
    else:
        added = candidates
    result += [e for e, _ in added]

    # Newest first; stable, and for equal years later (i.e. new) entries come first.
    final = [
        ordered(e)
        for _, e in sorted(
            ((i, e) for i, e in enumerate(result)),
            key=lambda t: (-int(t[1]["year"]), -t[0]),
        )
    ]

    print(f"\nORCID works considered: {total}")
    print(f"New entries: {len(added)}")
    for e, complete in added:
        flag = "" if complete else "   [authors incomplete]"
        print(f"  + [{e['year']}] {e['title']}{flag}\n      {e['authors']}")
    print(f"\nExisting entries with a filled-in DOI: {len(updated)}")
    for u in updated:
        print(f"  ~ {u}")
    if args.filter:
        print(f"\nRejected as unrelated to QIM: {len(rejected)}")
        for (e, _), reason in rejected:
            print(f"  - [{e['year']}] {e['title']}\n      reason: {reason}")
        if unclassified:
            print(f"\nCould not be classified (kept, please review): {len(unclassified)}")
            for (e, _), why in unclassified:
                print(f"  ? [{e['year']}] {e['title']}  ({why})")
    incomplete = sum(1 for _, c in added if not c)
    if added:
        print('\nNew entries have empty "keywords": please tag them by hand.')
    if incomplete:
        print(f"{incomplete} new entries have only the ORCID owner as author: complete them by hand.")

    if args.write:
        PUBS_FILE.write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote {PUBS_FILE}. Review with: git diff data/publications.json")
    else:
        print("\nDry run only. Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
