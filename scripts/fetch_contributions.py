#!/usr/bin/env python3

import json
import re
from collections import defaultdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = "adix4612-Devloper"

URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT = Path("data/contributions.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
}


# ============================================================
# FETCH GITHUB PAGE
# ============================================================

def fetch_html():
    print(f"[+] Fetching contributions for @{USERNAME}")
    print(f"[+] URL: {URL}")

    try:
        response = requests.get(
            URL,
            headers=HEADERS,
            timeout=30,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not connect to GitHub: {exc}"
        ) from exc

    print(f"[+] HTTP status: {response.status_code}")

    if response.status_code == 404:
        raise RuntimeError(
            "\n"
            "GitHub returned 404.\n\n"
            f"Check that the username is correct:\n"
            f"    {USERNAME}\n\n"
            f"Requested URL:\n"
            f"    {URL}\n"
        )

    response.raise_for_status()

    return response.text


# ============================================================
# PARSE CONTRIBUTION CELLS
# ============================================================

def parse_contributions(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    cells = soup.select(
        "td[data-date]"
    )

    if not cells:
        # Try the contribution graph's rect elements as a fallback.
        cells = soup.select(
            "[data-date][data-level]"
        )

    if not cells:
        raise RuntimeError(
            "No contribution cells were found.\n"
            "GitHub may have changed the contribution "
            "calendar HTML structure."
        )

    days = []

    for cell in cells:
        raw_date = cell.get(
            "data-date"
        )

        if not raw_date:
            continue

        raw_level = cell.get(
            "data-level",
            "0",
        )

        try:
            level = int(raw_level)
        except (ValueError, TypeError):
            level = 0

        level = max(
            0,
            min(5, level),
        )

        # GitHub commonly exposes contribution information
        # through aria-label.
        label = cell.get(
            "aria-label",
            "",
        )

        count = 0

        # Examples:
        # "15 contributions on January 1, 2026"
        # "1 contribution on January 2, 2026"
        # "No contributions on January 3, 2026"
        match = re.search(
            r"([\d,]+)\s+contribution",
            label,
            flags=re.IGNORECASE,
        )

        if match:
            count = int(
                match.group(1).replace(",", "")
            )

        elif "no contributions" in label.lower():
            count = 0

        days.append(
            {
                "date": raw_date,
                "count": count,
                "level": level,
                "label": label,
            }
        )

    # Remove duplicate dates.
    unique = {}

    for day in days:
        unique[day["date"]] = day

    return sorted(
        unique.values(),
        key=lambda item: item["date"],
    )


# ============================================================
# CALCULATE STATISTICS
# ============================================================

def calculate_stats(days):
    if not days:
        return {
            "total": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": None,
            "monthly_totals": {},
        }

    total = sum(
        day["count"]
        for day in days
    )

    # --------------------------------------------------------
    # Best day
    # --------------------------------------------------------

    best_day = max(
        days,
        key=lambda day: day["count"],
    )

    # --------------------------------------------------------
    # Longest streak
    # --------------------------------------------------------

    longest_streak = 0
    running_streak = 0

    for day in days:
        if day["count"] > 0:
            running_streak += 1

            longest_streak = max(
                longest_streak,
                running_streak,
            )
        else:
            running_streak = 0

    # --------------------------------------------------------
    # Current streak
    # --------------------------------------------------------

    current_streak = 0

    for day in reversed(days):
        if day["count"] > 0:
            current_streak += 1
        else:
            break

    # --------------------------------------------------------
    # Monthly totals
    # --------------------------------------------------------

    monthly_totals = defaultdict(int)

    for day in days:
        month = day["date"][:7]

        monthly_totals[month] += day["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": dict(
            monthly_totals
        ),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print(" GitHub Contribution Fetcher")
    print("=" * 60)

    html = fetch_html()

    print("[+] Parsing contribution calendar...")

    days = parse_contributions(html)

    print(
        f"[+] Parsed {len(days)} contribution days"
    )

    stats = calculate_stats(days)

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

    if stats["best_day"]:
        print(
            f"[+] Best day: "
            f"{stats['best_day']['count']:,} "
            f"contributions on "
            f"{stats['best_day']['date']}"
        )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "username": USERNAME,
        "source": URL,
        "days": days,
        "stats": stats,
    }

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"[+] Saved: {OUTPUT}"
    )

    print("=" * 60)
    print(" Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
