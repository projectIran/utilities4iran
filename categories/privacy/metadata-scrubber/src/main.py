#!/usr/bin/env python3
"""
metadata-scrubber: Recursively strip EXIF, XMP, IPTC, and PDF metadata.
All processing is done in-place via a clean rewrite — no temp files are left behind.
"""

import argparse
import sys
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
PDF_SUFFIX = ".pdf"


def scrub_image(path: Path) -> None:
    from PIL import Image

    with Image.open(path) as img:
        mode = img.mode
        data = img.tobytes()
        size = img.size

    # Reconstruct from raw pixel data — no metadata survives this round-trip.
    clean = Image.frombytes(mode, size, data)
    suffix = path.suffix.lower()
    if suffix in (".jpg", ".jpeg"):
        clean.save(path, format="JPEG", quality=95, exif=b"")
    else:
        clean.save(path, format="PNG")


def scrub_pdf(path: Path) -> None:
    import pikepdf

    with pikepdf.open(path, allow_overwriting_input=True) as pdf:
        # Remove document-level metadata streams and info dictionary.
        if "/Metadata" in pdf.Root:
            del pdf.Root["/Metadata"]
        if "/Info" in pdf.trailer:
            del pdf.trailer["/Info"]
        pdf.save(path)


def scrub_file(path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        scrub_image(path)
    elif suffix == PDF_SUFFIX:
        scrub_pdf(path)


def walk(target: Path):
    if target.is_file():
        yield target
    elif target.is_dir():
        for child in sorted(target.rglob("*")):
            if child.is_file():
                yield child


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Strip EXIF, XMP, IPTC, and PDF metadata from files."
    )
    parser.add_argument(
        "target",
        help="File or directory to process recursively.",
    )
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"Error: '{target}' does not exist.", file=sys.stderr)
        sys.exit(1)

    processed = 0
    for path in walk(target):
        suffix = path.suffix.lower()
        if suffix not in IMAGE_SUFFIXES and suffix != PDF_SUFFIX:
            continue
        try:
            scrub_file(path)
            print(f"[OK] Scrubbed: {path}")
            processed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Skipping {path}: {exc}", file=sys.stderr)

    if processed == 0:
        print("[INFO] No supported files found.", file=sys.stderr)


if __name__ == "__main__":
    main()
