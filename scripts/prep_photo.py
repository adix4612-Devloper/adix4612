#!/usr/bin/env python3

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


OUTPUT = Path("data/source-prepped.png")


def prepare_photo(input_path: str) -> None:
    input_file = Path(input_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Photo not found: {input_file}")

    print(f"[+] Loading {input_file}")

    image = Image.open(input_file).convert("RGBA")

    print("[+] Removing background...")
    cutout = remove(image)

    # White background.
    white = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    white.alpha_composite(cutout)

    rgb = white.convert("RGB")

    # Convert to OpenCV grayscale.
    cv_image = cv2.cvtColor(
        np.array(rgb),
        cv2.COLOR_RGB2GRAY,
    )

    print("[+] Applying local contrast enhancement...")

    clahe = cv2.createCLAHE(
        clipLimit=2.2,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(cv_image)

    # Slight sharpening.
    blurred = cv2.GaussianBlur(enhanced, (0, 0), 1.0)

    sharpened = cv2.addWeighted(
        enhanced,
        1.35,
        blurred,
        -0.35,
        0,
    )

    # Keep values in valid grayscale range.
    sharpened = np.clip(
        sharpened,
        0,
        255,
    ).astype(np.uint8)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result = Image.fromarray(
        sharpened,
        mode="L",
    )

    result.save(
        OUTPUT,
        optimize=True,
    )

    print(f"[+] Saved: {OUTPUT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python scripts/prep_photo.py source-photo.jpg"
        )
        sys.exit(1)

    prepare_photo(sys.argv[1])
