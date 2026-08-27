#!/usr/bin/env python3

import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "adix4612"

URL = (
    f"https://github.com/users/"
    f"{USERNAME}/contributions"
)

OUTPUT = Path("data/contributions.json")


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; GitHubProfileArt/1.0)"
    )
}


def fetch_html() -> str:
    print(f"[+] Fetching contributions for @{USERNAME}")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def parse_contributions(html: str) -> list[dict]:
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    cells = soup.select(
        "td[data-date]"
    )

    if not cells:
        raise RuntimeError(
            "No contribution cells found. "
            "GitHub may have changed the page markup."
        )

    days = []

    for cell in cells:
        raw_date = cell.get("data-date")

        if not raw_date:
            continue

        level = cell.get(
            "data-level",
            "0",
        )

        try:
            level = int(level)
        except ValueError:
            level = 0

        # GitHub sometimes includes aria-label text such as:
        # "15 contributions on January 1, 2026"
        label = cell.get(
            "aria-label",
            "",
        )

        match = re.search(
            r"([\d,]+)\s+contribution",
            label,
        )

        count = 0

        if match:
            count = int(
                match.group(1).replace(",", "")
            )

        days.append(
            {
                "date": raw_date,
                "count": count,
                "level": level,
            }
        )

    return days


def calculate_stats(days: list[dict]) -> dict:
    if not days:
        return {
            "total": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": None,
            "monthly_totals": {},
        }

    ordered = sorted(
        days,
        key=lambda x: x["date"],
    )

    total = sum(
        day["count"]
        for day in ordered
    )

    best = max(
        ordered,
        key=lambda x: x["count"],
    )

    # Calculate streaks.
    longest = 0
    current = 0
    running = 0

    for day in ordered:
        if day["count"] > 0:
            running += 1
            longest = max(
                longest,
                running,
            )
        else:
            running = 0

    # Current streak must be counted backwards.
    for day in reversed(ordered):
        if day["count"] > 0:
            current += 1
        else:
            break

    monthly = defaultdict(int)

    for day in ordered:
        month = day["date"][:7]
        monthly[month] += day["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly_totals": dict(monthly),
    }


def main():
    html = fetch_html()

    days = parse_contributions(html)

    stats = calculate_stats(days)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "username": USERNAME,
        "days": days,
        "stats": stats,
    }

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"[+] Parsed {len(days)} contribution days"
    )

    print(
        f"[+] Total contributions: "
        f"{stats['total']:,}"
    )

    print(
        f"[+] Current streak: "
        f"{stats['current_streak']} days"
    )

    print(
        f"[+] Longest streak: "
        f"{stats['longest_streak']} days"
    )

    print(f"[+] Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
