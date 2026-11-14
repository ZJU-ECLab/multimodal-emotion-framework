#!/usr/bin/env python3
"""Combine, clean, and summarize the article-level emotion CSV files.

The script uses only the Python standard library.  Paths default to the
organized project layout and can be overridden from the command line::

    python scripts/python/analyze_emotions.py

The combined file keeps every article, including an article whose labels are
all removed as non-emotional dimensions.  Such a row has an empty
``emotions_studied`` field and is excluded from the statistical denominator.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from emotion_label_rules import clean_label, normalize_label
from plot_style import article_label_colors, read_colors


COMBINED_FIELDS = ["id", "title", "emotions_studied"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BATCH1 = PROJECT_ROOT / "data/raw/labels/emotions_by_article.csv"
DEFAULT_BATCH2 = PROJECT_ROOT / "data/raw/labels/emotions_by_article_batch2.csv"
DEFAULT_TEXT1 = PROJECT_ROOT / "data/intermediate/text/batch1"
DEFAULT_TEXT2 = PROJECT_ROOT / "data/intermediate/text/batch2"
DEFAULT_TABLE_DIR = PROJECT_ROOT / "outputs/tables"
DEFAULT_STYLE = PROJECT_ROOT / "config/plot_style.csv"


def read_csv_rows(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path} has no data rows")
    return rows


def split_labels(value: str) -> List[str]:
    """Split a semicolon-separated field and preserve first occurrence order."""
    labels: List[str] = []
    seen = set()
    for item in (value or "").split(";"):
        label = item.strip()
        key = clean_label(label)
        if key and key not in seen:
            labels.append(label)
            seen.add(key)
    return labels


def title_from_batch2_id(article_id: str) -> str:
    title = article_id.replace("_", " ")
    return re.sub(r"\s+", " ", title).strip()


def title_key(title: str) -> str:
    """Normalize a title for conservative cross-batch duplicate matching."""
    text = unicodedata.normalize("NFKC", title).lower().replace("_", " ")
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def text_digest(path: Optional[Path]) -> Tuple[Optional[str], int]:
    """Return a whitespace/punctuation-insensitive text digest and character count."""
    if path is None or not path.exists():
        return None, 0
    text = path.read_text(encoding="utf-8", errors="ignore")
    normalized = unicodedata.normalize("NFKC", text).lower()
    normalized = re.sub(r"[^a-z0-9]+", "", normalized)
    if not normalized:
        return None, len(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest(), len(text)


def locate_text(text_dir: Path, source: str, article_id: str) -> Optional[Path]:
    index_path = PROJECT_ROOT / "references/articles.csv"
    with index_path.open(encoding="utf-8-sig", newline="") as handle:
        matches = [
            row for row in csv.DictReader(handle)
            if row["source"] == source and row["source_article_id"] == article_id
        ]
    if len(matches) != 1:
        raise ValueError(f"Reference index has {len(matches)} matches for {source}:{article_id}")
    path = text_dir / Path(matches[0]["text"]).name
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def load_records(batch1_path: Path, batch2_path: Path, txt1_dir: Path, txt2_dir: Path) -> List[dict]:
    records: List[dict] = []
    batch1_rows = read_csv_rows(batch1_path)
    required1 = {"article_id", "title", "emotions_studied"}
    if not required1.issubset(batch1_rows[0]):
        raise ValueError(f"{batch1_path} must contain {sorted(required1)}")
    for row in batch1_rows:
        article_id = row["article_id"].strip()
        text_path = locate_text(txt1_dir, "batch1", article_id)
        digest, text_chars = text_digest(text_path)
        records.append(
            {
                "source": "batch1",
                "source_article_id": article_id,
                "id": f"batch1_{article_id}",
                "title": row["title"].strip(),
                "raw_labels": split_labels(row.get("emotions_studied", "")),
                "title_key": title_key(row["title"]),
                "text_digest": digest,
                "text_chars": text_chars,
                "text_path": str(text_path) if text_path else "",
            }
        )

    batch2_rows = read_csv_rows(batch2_path)
    required2 = {"article_id", "emotions_studied"}
    if not required2.issubset(batch2_rows[0]):
        raise ValueError(f"{batch2_path} must contain {sorted(required2)}")
    for row in batch2_rows:
        article_id = row["article_id"].strip()
        title = title_from_batch2_id(article_id)
        text_path = locate_text(txt2_dir, "batch2", article_id)
        digest, text_chars = text_digest(text_path)
        records.append(
            {
                "source": "batch2",
                "source_article_id": article_id,
                "id": f"batch2_{article_id}",
                "title": title,
                "raw_labels": split_labels(row.get("emotions_studied", "")),
                "title_key": title_key(title),
                "text_digest": digest,
                "text_chars": text_chars,
                "text_path": str(text_path) if text_path else "",
            }
        )
    return records


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def duplicate_matches(records: Sequence[dict]) -> List[dict]:
    matches: List[dict] = []
    for left in range(len(records)):
        for right in range(left + 1, len(records)):
            first, second = records[left], records[right]
            if first["source"] == second["source"]:
                continue
            if first["title_key"] and first["title_key"] == second["title_key"]:
                matches.append(
                    {
                        "left": left,
                        "right": right,
                        "match_type": "exact_normalized_title",
                        "similarity": 1.0,
                    }
                )
                continue
            if (
                first["text_digest"]
                and first["text_digest"] == second["text_digest"]
                and min(first["text_chars"], second["text_chars"]) >= 500
            ):
                matches.append(
                    {
                        "left": left,
                        "right": right,
                        "match_type": "exact_normalized_text",
                        "similarity": 1.0,
                    }
                )
                continue
            if first["title_key"] and second["title_key"]:
                similarity = SequenceMatcher(
                    None, first["title_key"], second["title_key"]
                ).ratio()
                # Only use an extremely high title threshold as a duplicate
                # fallback; the text and exact-title checks remain primary.
                if similarity >= 0.98:
                    matches.append(
                        {
                            "left": left,
                            "right": right,
                            "match_type": "near_identical_normalized_title",
                            "similarity": similarity,
                        }
                    )
    return matches


def deduplicate(records: Sequence[dict]) -> Tuple[List[dict], List[dict], int]:
    matches = duplicate_matches(records)
    union_find = UnionFind(len(records))
    for match in matches:
        union_find.union(match["left"], match["right"])

    groups: Dict[int, List[int]] = defaultdict(list)
    for index in range(len(records)):
        groups[union_find.find(index)].append(index)

    deduplicated: List[dict] = []
    audit: List[dict] = []
    for indices in groups.values():
        ordered = sorted(indices, key=lambda i: (records[i]["source"] != "batch1", i))
        kept_index = ordered[0]
        kept = dict(records[kept_index])
        merged_labels: List[str] = []
        seen_labels = set()
        for index in ordered:
            for label in records[index]["raw_labels"]:
                key = clean_label(label)
                if key not in seen_labels:
                    merged_labels.append(label)
                    seen_labels.add(key)
        kept["raw_labels"] = merged_labels
        deduplicated.append(kept)
        for removed_index in ordered[1:]:
            matching = next(
                (
                    match
                    for match in matches
                    if {match["left"], match["right"]}
                    == {kept_index, removed_index}
                ),
                None,
            )
            audit.append(
                {
                    "kept_id": kept["id"],
                    "removed_id": records[removed_index]["id"],
                    "match_type": matching["match_type"] if matching else "transitive_match",
                    "similarity": f"{matching['similarity']:.6f}" if matching else "",
                    "kept_title": kept["title"],
                    "removed_title": records[removed_index]["title"],
                }
            )
    deduplicated.sort(key=lambda row: (row["source"] != "batch1", row["source_article_id"]))
    return deduplicated, audit, len(records) - len(deduplicated)


def normalize_records(records: Sequence[dict]) -> Tuple[List[dict], List[dict], Dict[str, int]]:
    audit: Dict[str, dict] = {}
    normalized_records: List[dict] = []
    counts = Counter()
    for record in records:
        canonical_labels: List[str] = []
        seen_canonical = set()
        for raw_label in record["raw_labels"]:
            canonical, action, reason = normalize_label(raw_label)
            raw_key = clean_label(raw_label)
            entry = audit.setdefault(
                raw_key,
                {
                    "raw_label": raw_label.strip(),
                    "canonical_label": canonical or "",
                    "action": action,
                    "reason": reason,
                    "article_ids": set(),
                    "mentions": 0,
                },
            )
            entry["article_ids"].add(record["id"])
            entry["mentions"] += 1
            counts[action] += 1
            if canonical and canonical not in seen_canonical:
                canonical_labels.append(canonical)
                seen_canonical.add(canonical)
        normalized = dict(record)
        normalized["canonical_labels"] = canonical_labels
        normalized_records.append(normalized)

    audit_rows = []
    for key in sorted(audit):
        entry = audit[key]
        audit_rows.append(
            {
                "raw_label": entry["raw_label"],
                "canonical_label": entry["canonical_label"],
                "action": entry["action"],
                "reason": entry["reason"],
                "article_count": len(entry["article_ids"]),
                "mentions": entry["mentions"],
            }
        )
    return normalized_records, audit_rows, dict(counts)


def write_csv(path: Path, fields: Sequence[str], rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def label_statistics(records: Sequence[dict]) -> Tuple[List[dict], List[dict], int]:
    statistical_records = [record for record in records if record["canonical_labels"]]
    article_counts = Counter()
    long_rows: List[dict] = []
    for record in statistical_records:
        for label in record["canonical_labels"]:
            article_counts[label] += 1
            long_rows.append(
                {"id": record["id"], "title": record["title"], "emotion_label": label}
            )
    total_articles = len(statistical_records)
    total_article_label_counts = sum(article_counts.values())
    ranked = sorted(article_counts.items(), key=lambda item: (-item[1], item[0]))
    rows = []
    for rank, (label, count) in enumerate(ranked, start=1):
        rows.append(
            {
                "rank": rank,
                "emotion_label": label,
                "article_count": count,
                "article_percentage": f"{100 * count / total_articles:.2f}" if total_articles else "0.00",
                "count_share_percentage": (
                    f"{100 * count / total_article_label_counts:.2f}"
                    if total_article_label_counts
                    else "0.00"
                ),
            }
        )
    return rows, long_rows, total_article_label_counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch1", type=Path, default=DEFAULT_BATCH1)
    parser.add_argument("--batch2", type=Path, default=DEFAULT_BATCH2)
    parser.add_argument("--txt1-dir", type=Path, default=DEFAULT_TEXT1)
    parser.add_argument("--txt2-dir", type=Path, default=DEFAULT_TEXT2)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_TABLE_DIR)
    parser.add_argument("--style", type=Path, default=DEFAULT_STYLE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_records(args.batch1, args.batch2, args.txt1_dir, args.txt2_dir)
    articles_before_deduplication = len(records)
    records, duplicate_rows, duplicate_removed = deduplicate(records)
    records, label_audit_rows, action_counts = normalize_records(records)
    stats_rows, long_rows, total_article_label_counts = label_statistics(records)
    articles_with_labels = sum(bool(record["canonical_labels"]) for record in records)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    combined_rows = [
        {
            "id": record["id"],
            "title": record["title"],
            "emotions_studied": "; ".join(record["canonical_labels"]),
        }
        for record in records
    ]
    write_csv(args.output_dir / "combined_emotions_by_article.csv", COMBINED_FIELDS, combined_rows)
    write_csv(
        args.output_dir / "emotion_label_statistics.csv",
        [
            "rank",
            "emotion_label",
            "article_count",
            "article_percentage",
            "count_share_percentage",
        ],
        stats_rows,
    )
    write_csv(
        args.output_dir / "article_emotion_labels_long.csv",
        ["id", "title", "emotion_label"],
        long_rows,
    )
    write_csv(
        args.output_dir / "emotion_label_audit.csv",
        ["raw_label", "canonical_label", "action", "reason", "article_count", "mentions"],
        label_audit_rows,
    )
    write_csv(
        args.output_dir / "duplicate_audit.csv",
        ["kept_id", "removed_id", "match_type", "similarity", "kept_title", "removed_title"],
        duplicate_rows,
    )
    no_labels = [
        {"id": record["id"], "title": record["title"]}
        for record in records
        if not record["canonical_labels"]
    ]
    write_csv(args.output_dir / "articles_without_emotion_labels.csv", ["id", "title"], no_labels)

    text_available = sum(bool(record["text_path"]) for record in records)
    text_missing = len(records) - text_available
    summary_rows = [
        {"metric": "articles_before_deduplication", "value": articles_before_deduplication},
        {"metric": "articles_after_deduplication", "value": len(records)},
        {"metric": "duplicate_articles_removed", "value": duplicate_removed},
        {"metric": "text_extracts_available", "value": text_available},
        {"metric": "text_extracts_missing", "value": text_missing},
        {"metric": "articles_in_statistical_denominator", "value": articles_with_labels},
        {"metric": "articles_excluded_from_statistics", "value": len(records) - articles_with_labels},
        {"metric": "unique_canonical_emotion_labels", "value": len(stats_rows)},
        {"metric": "total_article_label_pairs", "value": total_article_label_counts},
        {"metric": "articles_without_emotion_labels", "value": len(no_labels)},
        {"metric": "raw_labels_mapped", "value": action_counts.get("map", 0)},
        {"metric": "raw_labels_kept", "value": action_counts.get("keep", 0)},
        {"metric": "raw_labels_removed", "value": action_counts.get("remove", 0)},
    ]
    write_csv(args.output_dir / "emotion_summary.csv", ["metric", "value"], summary_rows)
    colors = read_colors(args.style)
    color_rows = article_label_colors(stats_rows, colors)
    label_colors = {row["emotion_label"]: row["color"] for row in color_rows}
    write_csv(
        args.output_dir / "emotion_label_color_map.csv",
        ["rank", "emotion_label", "article_count", "frequency_band", "color_order", "color"],
        color_rows,
    )
    print(f"Articles: {len(records)} after deduplication ({duplicate_removed} removed)")
    print(f"Statistical denominator: {articles_with_labels} articles with retained labels")
    print(f"Canonical labels: {len(stats_rows)}; article-label pairs: {total_article_label_counts}")
    print(f"Articles with no retained emotion labels: {len(no_labels)}")
    print(f"Text extracts unavailable for {text_missing} articles")
    print(f"Tables written to {args.output_dir}")


if __name__ == "__main__":
    main()
