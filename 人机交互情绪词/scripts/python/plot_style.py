"""Load the palette shared by the Python and R plotting scripts."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Sequence


def read_colors(path: Path) -> Dict[str, str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        return {
            f"{row['role']}.{row['key']}": row["color"]
            for row in rows
        }


def frequency_band(value: int, is_other: bool = False) -> str:
    if is_other or value < 5:
        return "under-5"
    if value >= 30:
        return "30-plus"
    if value >= 20:
        return "20-29"
    if value >= 15:
        return "15-19"
    if value >= 10:
        return "10-14"
    if value >= 7:
        return "7-9"
    return "5-6"


def _gradient_color(value: float, stops: Sequence[tuple[float, str]]) -> str:
    if value <= stops[0][0]:
        return stops[0][1]
    for (left_value, left_color), (right_value, right_color) in zip(stops, stops[1:]):
        if value <= right_value:
            left_rgb = tuple(int(left_color[index:index + 2], 16) for index in (1, 3, 5))
            right_rgb = tuple(int(right_color[index:index + 2], 16) for index in (1, 3, 5))
            fraction = (value - left_value) / (right_value - left_value)
            return "#" + "".join(
                f"{round(left + (right - left) * fraction):02X}"
                for left, right in zip(left_rgb, right_rgb)
            )
    return stops[-1][1]


def article_label_colors(
    stats: Sequence[dict], colors: Dict[str, str]
) -> List[dict]:
    """Assign distinct adjacent shades along the count-ranked label order."""
    bands = [frequency_band(int(row["article_count"])) for row in stats]
    counts = [int(row["article_count"]) for row in stats]
    ranks = list(range(1, len(stats) + 1))

    def first_rank(predicate) -> int:
        return next(rank for rank, count in zip(ranks, counts) if predicate(count))

    def last_rank(predicate) -> int:
        return max(rank for rank, count in zip(ranks, counts) if predicate(count))

    stops = [
        (1.0, colors["gradient.high"]),
        (float(last_rank(lambda count: count >= 30)), colors["gradient.high-warm"]),
        (float(last_rank(lambda count: count >= 20)), colors["gradient.warm"]),
        (float(first_rank(lambda count: count < 20)), colors["gradient.warm-green"]),
        (float(first_rank(lambda count: count < 15)), colors["gradient.green"]),
        (float(last_rank(lambda count: count >= 10)), colors["gradient.green-cyan"]),
        (float(last_rank(lambda count: count >= 10) + 1), colors["gradient.cyan"]),
        (float(last_rank(lambda count: count >= 7)), colors["gradient.cyan-blue"]),
        (float(last_rank(lambda count: count >= 5)), colors["gradient.purple"]),
        (float(first_rank(lambda count: count < 5)), colors["gradient.low"]),
        (float(len(stats)), colors["gradient.other"]),
    ]
    stops = sorted(stops, key=lambda item: item[0])
    result = [_gradient_color(float(rank), stops) for rank in ranks]
    return [
        {
            "rank": row["rank"],
            "emotion_label": row["emotion_label"],
            "article_count": row["article_count"],
            "frequency_band": band,
            "color_order": rank,
            "color": color,
        }
        for row, band, rank, color in zip(stats, bands, ranks, result)
    ]
