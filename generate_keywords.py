import json
import ollama
import sys
from pathlib import Path


PUBLICATIONS_PATH = "data/publications.json"
MODEL = "llama3.2"
N_KEYWORDS = 4


def extract_keywords(title: str, n: int = N_KEYWORDS) -> list[str]:
    prompt = f"""Extract between 1 and {n} broad, generic keywords from this academic paper title.
Only include keywords that are clearly relevant — do not force {n} keywords if fewer are sufficient.

Rules:
- Keywords must be general field-level concepts, not specific method names or dataset names
- Good examples: 'deep learning', 'X-ray tomography', 'fiber analysis', 'image segmentation'
- Bad examples: 'U-Net architecture', 'Stevns Klint chalk', 'phase-contrast holography'
- Keywords can be 1 or 2 words
- Return only a valid JSON list of strings, nothing else, no explanation

Title: {title}"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response['message']['content'].strip()
    keywords = json.loads(content)

    if not isinstance(keywords, list):
        raise ValueError(f"Expected a list, got: {type(keywords)}")

    return keywords[:n]


def update_keywords(publications_path: str = PUBLICATIONS_PATH, force: bool = False):
    """
    Load publications JSON, generate keywords for papers that don't have them,
    and save back to the same file.
    Use force=True to regenerate keywords for all papers including existing ones.
    """
    path = Path(publications_path)

    if not path.exists():
        raise FileNotFoundError(f"Publications file not found: {publications_path}")

    with open(path) as f:
        papers = json.load(f)

    total   = len(papers)
    skipped = 0
    updated = 0
    failed  = 0

    print(f"Found {total} papers in {publications_path}")
    print(f"Model: {MODEL} | Keywords per paper: {N_KEYWORDS}")
    if force:
        print("Mode: FORCE — regenerating all keywords")
    print("-" * 60)

    for paper in papers:
        title = paper.get("title", "")

        if not title:
            print(f"Skipping entry with no title")
            skipped += 1
            continue

        if "keywords" in paper and not force:
            print(f"→ Skip (already has keywords): {title[:60]}")
            skipped += 1
            continue

        try:
            keywords = extract_keywords(title)
            paper["keywords"] = keywords
            updated += 1
            print(f"✓ {title[:60]}")
            print(f"  → {keywords}")

        except Exception as e:
            print(f"Failed: {title[:60]}")
            print(f"  Error: {e}")
            failed += 1

    with open(path, "w") as f:
        json.dump(papers, f, indent=2)

    print("-" * 60)
    print(f"Done.")
    print(f"  Updated : {updated}")
    print(f"  Skipped : {skipped}")
    print(f"  Failed  : {failed}")


if __name__ == "__main__":
    force = "--force" in sys.argv
    update_keywords(force=force)