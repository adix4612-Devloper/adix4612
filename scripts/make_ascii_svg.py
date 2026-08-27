#!/usr/bin/env python3

from pathlib import Path

from PIL import Image


SOURCE = Path("data/source-prepped.png")
OUTPUT = Path("avi-ascii.svg")

# Bright -> dark.
RAMP = " .`:-=+*cs#%@"

# Portrait dimensions.
COLS = 100
ROWS = 53

# SVG appearance.
FONT_SIZE = 8
CHAR_WIDTH = 5.2
LINE_HEIGHT = 9.2

TEXT_COLOR = "#c9d1d9"
BACKGROUND = "#0d1117"

# Animation.
ROW_DELAY = 0.055
ROW_DURATION = 0.42


def xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def image_to_ascii(image: Image.Image) -> list[str]:
    image = image.convert("L")

    # Characters are taller than they are wide, so compensate vertically.
    resized = image.resize(
        (COLS, ROWS),
        Image.Resampling.LANCZOS,
    )

    pixels = list(resized.getdata())

    lines = []

    for row in range(ROWS):
        chars = []

        for col in range(COLS):
            brightness = pixels[row * COLS + col]

            index = int(
                brightness / 255 * (len(RAMP) - 1)
            )

            chars.append(RAMP[index])

        lines.append("".join(chars).rstrip())

    return lines


def make_svg(lines: list[str]) -> str:
    width = int(COLS * CHAR_WIDTH + 10)
    height = int(ROWS * LINE_HEIGHT + 10)

    parts = [
        f'''<svg xmlns="http://www.w3.org/2000/svg"
             width="{width}"
             height="{height}"
             viewBox="0 0 {width} {height}"
             role="img"
             aria-label="Animated ASCII portrait">

<style>
.ascii-row {{
    font-family: "Courier New", Courier, monospace;
    font-size: {FONT_SIZE}px;
    font-weight: 600;
    fill: {TEXT_COLOR};
}}

@keyframes reveal {{
    0% {{
        opacity: 0;
        transform: translateX(-12px);
    }}

    100% {{
        opacity: 1;
        transform: translateX(0);
    }}
}}

.row {{
    opacity: 0;
    animation-name: reveal;
    animation-duration: {ROW_DURATION}s;
    animation-timing-function: ease-out;
    animation-fill-mode: forwards;
}}
</style>

<rect
    width="100%"
    height="100%"
    rx="8"
    fill="{BACKGROUND}"
/>
'''
    ]

    for row, line in enumerate(lines):
        y = 9 + row * LINE_HEIGHT
        delay = row * ROW_DELAY

        safe_line = xml_escape(line)

        parts.append(
            f'''<text
    class="ascii-row row"
    x="5"
    y="{y:.2f}"
    style="animation-delay:{delay:.3f}s"
>{safe_line}</text>
'''
        )

    parts.append("</svg>")

    return "".join(parts)


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"{SOURCE} not found. "
            "Run prep_photo.py first."
        )

    print("[+] Reading prepared image...")

    image = Image.open(SOURCE)

    print(
        f"[+] Converting image to "
        f"{COLS}x{ROWS} ASCII..."
    )

    lines = image_to_ascii(image)

    print("[+] Building SVG...")

    svg = make_svg(lines)

    OUTPUT.write_text(
        svg,
        encoding="utf-8",
    )

    print(f"[+] Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
