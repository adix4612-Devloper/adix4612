#!/usr/bin/env python3

import os
from pathlib import Path


OUTPUT = Path("info-card.svg")

USERNAME = "adix4612"

ROLE = "Developer"

STACK = [
    "Python",
    "Streamlit",
    "Data Analytics",
    "Cybersecurity",
]

FOCUS = [
    "Building useful software",
    "Automation & data",
    "Learning every day",
]

LOCATION = "India"

WIDTH = 490
HEIGHT = 370


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def add_line(
    parts,
    key,
    value,
    y,
    delay,
):
    parts.append(
        f'''
<g class="line" style="animation-delay:{delay:.2f}s">
    <text
        x="30"
        y="{y}"
        class="key"
    >{esc(key)}</text>

    <text
        x="145"
        y="{y}"
        class="value"
    >{esc(value)}</text>
</g>
'''
    )


def main():
    static = os.getenv("STATIC", "0") == "1"

    parts = [
        f'''<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    role="img"
    aria-label="Developer information card"
>

<style>
.card {{
    fill: #0d1117;
}}

.border {{
    fill: none;
    stroke: #30363d;
    stroke-width: 1;
}}

.title {{
    font-family: monospace;
    font-size: 14px;
    font-weight: bold;
    fill: #58a6ff;
}}

.key {{
    font-family: monospace;
    font-size: 13px;
    font-weight: bold;
    fill: #39d353;
}}

.value {{
    font-family: monospace;
    font-size: 13px;
    fill: #c9d1d9;
}}

.muted {{
    font-family: monospace;
    font-size: 11px;
    fill: #8b949e;
}}

.line {{
    opacity: 0;
    animation: appear 0.4s ease-out forwards;
}}

@keyframes appear {{
    from {{
        opacity: 0;
        transform: translateX(-10px);
    }}

    to {{
        opacity: 1;
        transform: translateX(0);
    }}
}}
</style>

<rect
    class="card"
    width="{WIDTH}"
    height="{HEIGHT}"
    rx="10"
/>

<rect
    class="border"
    x="0.5"
    y="0.5"
    width="{WIDTH - 1}"
    height="{HEIGHT - 1}"
    rx="10"
/>

<circle cx="20" cy="22" r="5" fill="#ff5f56"/>
<circle cx="38" cy="22" r="5" fill="#ffbd2e"/>
<circle cx="56" cy="22" r="5" fill="#27c93f"/>

<text
    x="78"
    y="27"
    class="title"
>adix4612@github:~</text>

<line
    x1="20"
    y1="48"
    x2="{WIDTH - 20}"
    y2="48"
    stroke="#30363d"
/>
'''
    ]

    y = 80
    delay = 0.15

    add_line(
        parts,
        "USER",
        USERNAME,
        y,
        delay,
    )

    y += 29
    delay += 0.08

    add_line(
        parts,
        "ROLE",
        ROLE,
        y,
        delay,
    )

    y += 29
    delay += 0.08

    add_line(
        parts,
        "LOCATION",
        LOCATION,
        y,
        delay,
    )

    y += 42

    parts.append(
        f'''
<text
    x="30"
    y="{y}"
    class="key"
>STACK</text>
'''
    )

    y += 27

    for item in STACK:
        add_line(
            parts,
            "",
            "• " + item,
            y,
            delay,
        )

        y += 23
        delay += 0.07

    y += 10

    parts.append(
        f'''
<text
    x="30"
    y="{y}"
    class="key"
>FOCUS</text>
'''
    )

    y += 27

    for item in FOCUS:
        add_line(
            parts,
            "",
            "• " + item,
            y,
            delay,
        )

        y += 23
        delay += 0.07

    parts.append(
        f'''
<text
    x="30"
    y="{HEIGHT - 18}"
    class="muted"
>status: online • building things • learning</text>
'''
    )

    parts.append("</svg>")

    svg = "".join(parts)

    # Static mode removes animations.
    if static:
        svg = svg.replace(
            'opacity: 0;',
            'opacity: 1;',
        )

        svg = svg.replace(
            'animation: appear 0.4s ease-out forwards;',
            'animation: none;',
        )

    OUTPUT.write_text(
        svg,
        encoding="utf-8",
    )

    print(f"[+] Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
