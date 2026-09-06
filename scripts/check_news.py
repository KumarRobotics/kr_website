#!/usr/bin/env python3
"""News lint checks

Run locally (python3 scripts/check_news.py, needs Pillow) and in CI
(.github/workflows/lint.yml). Exits non-zero if any check fails.

Checks:
1. items    Every {{< newsitem >}} shortcode in content/ must have a
             non-empty title and a non-empty image, and the image file
             must exist under static/.
2. images   Each referenced image must be a valid image, 300-750 px
             wide, at most 500 KB, with a height/width ratio between
             0.3 and 1.4. Widths below 600 px are reported as notes
             (not failures).
"""

import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)

# {{< newsitem ... >}} block; attributes sit on their own lines.
ITEM_RE = re.compile(r"\{\{<\s*newsitem\b(?P<body>.*?)>\}\}", re.DOTALL)
# key="value" attributes anywhere in the block; values hold no quotes.
ATTR_RE = re.compile(r"(?P<key>\w+)\s*=\s*\"(?P<val>[^\"]*)\"")

MIN_W = 300      # px, hard lower bound
MAX_W = 750      # px, hard upper bound
NOTE_W = 600     # px, report (not fail) below this width
MAX_BYTES = 500 * 1024
MIN_RATIO = 0.3   # h/w, hard lower bound
MAX_RATIO = 1.4  # h/w, hard upper bound


def parse_items(text):
    """Yield (start_line, attrs) for every newsitem shortcode in text."""
    for m in ITEM_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        attrs = {}
        for am in ATTR_RE.finditer(m.group("body")):
            attrs[am.group("key")] = am.group("val")
        yield line, attrs


def check_file(path, errors, notes, Image):
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    checked = 0
    for line, attrs in parse_items(text):
        checked += 1
        if not attrs.get("title", "").strip():
            errors.append(f"{path}:{line}: newsitem missing title")
        image = attrs.get("image", "").strip()
        if not image:
            errors.append(f"{path}:{line}: newsitem missing image")
            continue
        fspath = os.path.join("static", image.lstrip("/"))
        if not os.path.isfile(fspath):
            errors.append(f"{path}:{line}: newsitem image {image} not found under static/")
            continue
        nbytes = os.path.getsize(fspath)
        if nbytes > MAX_BYTES:
            errors.append(f"{path}:{line}: image {image} is {nbytes / 1024:.0f} KB, "
                          f"must be at most {MAX_BYTES // 1024} KB")
        if Image is None:
            continue
        try:
            with Image.open(fspath) as im:
                im.load()
                w, h = im.size
        except Exception:
            errors.append(f"{path}:{line}: image {image} is not a valid image")
            continue
        if w < MIN_W:
            errors.append(f"{path}:{line}: image {image} is {w} px wide, "
                          f"must be at least {MIN_W} px")
        elif w > MAX_W:
            errors.append(f"{path}:{line}: image {image} is {w} px wide, "
                          f"must be at most {MAX_W} px")
        elif w < NOTE_W:
            notes.append(f"{path}:{line}: image {image} is {w} px wide, "
                          f"below {NOTE_W} px")
        ratio = h / w
        if ratio < MIN_RATIO:
            errors.append(f"{path}:{line}: image {image} has h/w ratio {ratio:.2f}, "
                          f"must be at least {MIN_RATIO}")
        elif ratio > MAX_RATIO:
            errors.append(f"{path}:{line}: image {image} has h/w ratio {ratio:.2f}, "
                          f"must be at most {MAX_RATIO}")
    return checked


def main():
    try:
        from PIL import Image
    except ImportError:
        Image = None

    errors, notes = [], []
    checked = 0
    for path in sorted(glob.glob("content/**/*.md", recursive=True)):
        checked += check_file(path, errors, notes, Image)

    if Image is None:
        notes.append("news: Pillow not installed, image checks skipped")
    print(f"note: news: {checked} newsitem(s) checked")
    for n in notes:
        print(f"note: {n}")
    if errors:
        print()
        for e in errors:
            print(f"ERROR: {e}")
        print(f"\n{len(errors)} error(s)")
        return 1
    print("\nall news checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
