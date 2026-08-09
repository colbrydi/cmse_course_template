#!/usr/bin/env python3
"""
Create a favicon.ico from an image.

Examples
--------
python make_favicon.py logo.png
python make_favicon.py logo.png --output docs/favicon.ico
"""

from pathlib import Path
import argparse

from PIL import Image


def create_favicon(input_file: Path, output_file: Path):
    """Create a favicon.ico from an input image."""

    img = Image.open(input_file).convert("RGBA")

    # Crop to a centered square
    w, h = img.size
    side = min(w, h)

    left = (w - side) // 2
    top = (h - side) // 2

    img = img.crop((left, top, left + side, top + side))

    # Sizes typically embedded in favicon files
    sizes = [
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256),
    ]

    img.save(output_file, format="ICO", sizes=sizes)

    print(f"✓ Created {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a favicon.ico file from an image."
    )

    parser.add_argument(
        "image",
        help="Input image file (PNG, JPEG, SVG rendered to PNG, etc.)",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="favicon.ico",
        help="Output favicon filename (default: favicon.ico)",
    )

    args = parser.parse_args()

    create_favicon(Path(args.image), Path(args.output))


if __name__ == "__main__":
    main()