import json
from pathlib import Path
from collections import Counter
import re


PUBLICATIONS_PATH = "data/publications.json"


def normalize(keyword: str) -> str:
    """Lowercase and strip for comparison."""
    return keyword.lower().strip()


def load_keywords(publications_path: str) -> tuple[list[dict], list[str]]:
    """Load papers and extract all keywords."""
    with open(publications_path) as f:
        papers = json.load(f)

    all_keywords = []
    for paper in papers:
        for kw in paper.get("keywords", []):
            all_keywords.append(normalize(kw))

    return papers, all_keywords


def report_coverage(papers: list[dict]):
    """How many papers have keywords."""
    total        = len(papers)
    with_kw      = sum(1 for p in papers if "keywords" in p and len(p["keywords"]) > 0)
    without_kw   = total - with_kw

    print("=" * 60)
    print("COVERAGE")
    print("=" * 60)
    print(f"  Total papers       : {total}")
    print(f"  With keywords      : {with_kw} ({100 * with_kw / total:.1f}%)")
    print(f"  Without keywords   : {without_kw} ({100 * without_kw / total:.1f}%)")

    # Distribution of keyword counts
    counts = Counter(len(p.get("keywords", [])) for p in papers)
    print(f"\n  Keyword count distribution:")
    for n in sorted(counts):
        print(f"    {n} keywords : {counts[n]} papers")


def report_frequency(all_keywords: list[str], top_n: int = 20):
    """Most and least common keywords."""
    freq = Counter(all_keywords)

    print("\n" + "=" * 60)
    print("FREQUENCY")
    print("=" * 60)
    print(f"  Total keywords (with duplicates) : {len(all_keywords)}")
    print(f"  Unique keywords                  : {len(freq)}")
    print(f"  Diversity ratio                  : {len(freq) / max(len(all_keywords), 1):.2f}  (1.0 = all unique)")

    print(f"\n  Top {top_n} most common keywords:")
    for kw, count in freq.most_common(top_n):
        bar = "█" * count
        print(f"    {kw:<35} {count:>3}x  {bar}")

    print(f"\n  Keywords appearing only once (too specific?):")
    singletons = [kw for kw, count in freq.items() if count == 1]
    for kw in sorted(singletons)[:20]:
        print(f"    - {kw}")
    if len(singletons) > 20:
        print(f"    ... and {len(singletons) - 20} more")


def report_near_duplicates(all_keywords: list[str]):
    """Find keywords that are likely the same but written differently."""
    unique = list(set(all_keywords))

    print("\n" + "=" * 60)
    print("NEAR DUPLICATES")
    print("=" * 60)

    # Remove spaces, hyphens, check for substring matches
    groups = {}
    for kw in unique:
        # Normalize aggressively for comparison
        key = re.sub(r'[-\s]', '', kw).lower()
        key = key.replace('fibre', 'fiber')   # common variant
        key = key.replace('colour', 'color')
        if key not in groups:
            groups[key] = []
        groups[key].append(kw)

    duplicates_found = False
    for key, variants in groups.items():
        if len(variants) > 1:
            print(f"  Possible duplicates: {variants}")
            duplicates_found = True

    if not duplicates_found:
        print("  No near-duplicates found.")


def report_word_length(all_keywords: list[str]):
    """Distribution of 1-word vs 2-word keywords."""
    one_word = [kw for kw in all_keywords if len(kw.split()) == 1]
    two_word  = [kw for kw in all_keywords if len(kw.split()) == 2]
    other     = [kw for kw in all_keywords if len(kw.split()) > 2]

    total = len(all_keywords)
    print("\n" + "=" * 60)
    print("KEYWORD LENGTH")
    print("=" * 60)
    print(f"  1-word keywords : {len(one_word):>4} ({100 * len(one_word) / total:.1f}%)")
    print(f"  2-word keywords : {len(two_word):>4} ({100 * len(two_word) / total:.1f}%)")
    if other:
        print(f"  3+ word keywords: {len(other):>4} ({100 * len(other) / total:.1f}%)  ← may be too specific")


def report_cooccurrence(papers: list[dict], top_n: int = 10):
    """Which keywords appear together most often."""
    from itertools import combinations

    pair_counts = Counter()
    for paper in papers:
        keywords = [normalize(kw) for kw in paper.get("keywords", [])]
        for pair in combinations(sorted(keywords), 2):
            pair_counts[pair] += 1

    print("\n" + "=" * 60)
    print("CO-OCCURRENCE (keywords that appear together)")
    print("=" * 60)
    if not pair_counts:
        print("  Not enough data.")
        return

    print(f"  Top {top_n} keyword pairs:")
    for (kw1, kw2), count in pair_counts.most_common(top_n):
        print(f"    '{kw1}' + '{kw2}' → {count} papers")




def run_evaluation(publications_path: str = PUBLICATIONS_PATH):
    papers, all_keywords = load_keywords(publications_path)

    report_coverage(papers)
    report_frequency(all_keywords)
    report_near_duplicates(all_keywords)
    report_word_length(all_keywords)
    report_cooccurrence(papers)

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_evaluation()