#!/usr/bin/env python3
"""Image lint checks for the Kumar Robotics website.

Run locally (python3 scripts/check_images.py, needs Pillow) and in CI
(.github/workflows/lint.yml). Exits non-zero if any check fails.

Checks:
1. refs      Every /img/... reference in content/, data/, layouts/, hugo.toml
             and static/css must resolve to an existing file under static/.
             Catches typos, broken renames and forgotten files.
2. members   Every photo in static/img/group/current/ must be exactly
             600x600 px and at most 500 KB.
"""

import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)

MEMBER_DIR = "static/img/group/current"
MEMBER_SIZE = (600, 600)
MEMBER_MAX_BYTES = 500 * 1024

# Quoted attribute values may contain spaces/parens (e.g. image="/img/x.jpg"),
# including comma-separated lists (e.g. the gallery images="a, b" attribute).
QUOTED_REF = re.compile(r"/img/[^\"\n]+")
# Unquoted contexts (YAML values, markdown links) -- no spaces allowed.
BARE_REF = re.compile(r"/img/[A-Za-z0-9_./@()-]+")


def collect_refs():
    files = (glob.glob("content/**/*.md", recursive=True)
             + glob.glob("layouts/**/*.html", recursive=True)
             + glob.glob("data/**/*", recursive=True)
             + ["hugo.toml", "static/css/custom.css"])
    refs = {}
    for f in files:
        if not os.path.isfile(f):
            continue
        text = open(f, encoding="utf-8", errors="ignore").read()
        matches = set()
        for m in QUOTED_REF.findall(text):
            for piece in m.split(","):
                piece = piece.strip().rstrip(") \t")
                if piece.startswith("/img/"):
                    matches.add(piece)
        matches |= set(BARE_REF.findall(text))
        for r in matches:
            refs.setdefault(r, []).append(f)
    return refs


def check_refs(errors, notes):
    refs = collect_refs()
    # Bare matches truncated at whitespace are prefixes of the full quoted
    # reference -- drop them instead of reporting phantom missing files.
    all_refs = sorted(refs)
    for r in all_refs:
        if any(o != r and o.startswith(r) for o in all_refs):
            continue
        if not os.path.exists(os.path.join("static", r.lstrip("/"))):
            errors.append(f"{r}: referenced in {refs[r][0]} but missing from static/")
    notes.append(f"refs: {len(all_refs)} image references checked")


def check_members(errors, notes):
    try:
        from PIL import Image
    except ImportError:
        notes.append("members: Pillow not installed, check skipped")
        return

    for name in sorted(os.listdir(MEMBER_DIR)):
        path = os.path.join(MEMBER_DIR, name)
        if not os.path.isfile(path):
            continue
        try:
            im = Image.open(path)
            im.load()
        except Exception:
            errors.append(f"{MEMBER_DIR}/{name}: not a valid image")
            continue
        if im.size != MEMBER_SIZE:
            errors.append(f"{MEMBER_DIR}/{name}: {im.size[0]}x{im.size[1]} px, "
                          "member photos must be exactly 600x600")
        kb = os.path.getsize(path) / 1024
        if os.path.getsize(path) > MEMBER_MAX_BYTES:
            errors.append(f"{MEMBER_DIR}/{name}: {kb:.0f} KB, "
                          "member photos must be at most 500 KB")


def main():
    errors, notes = [], []
    check_refs(errors, notes)
    check_members(errors, notes)

    for n in notes:
        print(f"note: {n}")
    if errors:
        print()
        for e in errors:
            print(f"ERROR: {e}")
        print(f"\n{len(errors)} error(s)")
        return 1
    print("\nall image checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
