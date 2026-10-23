#!/usr/bin/env python3
"""Repack an upstream Ruff wheel with the cross-compiled z/OS executable."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import re
import zipfile
from pathlib import Path


def digest(data: bytes) -> str:
    value = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
    return f"sha256={value.decode()}"


def build(source: Path, binary: Path, output: Path, python_tag: str, platform: str) -> None:
    dist_info = "ruff-0.17.2.dist-info"
    script = "ruff-0.17.2.data/scripts/ruff"
    wheel_metadata = f"{dist_info}/WHEEL"
    record = f"{dist_info}/RECORD"

    entries: dict[str, tuple[bytes, int]] = {}
    with zipfile.ZipFile(source) as archive:
        for info in archive.infolist():
            if info.filename in {script, wheel_metadata, record}:
                continue
            entries[info.filename] = (archive.read(info), info.external_attr)

        metadata = archive.read(wheel_metadata).decode("utf-8")

    metadata = re.sub(
        r"(?m)^Tag:.*(?:\nTag:.*)*$",
        f"Tag: {python_tag}-none-{platform}",
        metadata,
    )
    entries[wheel_metadata] = (metadata.encode(), 0o100644 << 16)
    entries[script] = (binary.read_bytes(), 0o100755 << 16)

    rows: list[list[str]] = []
    for name in sorted(entries):
        data, _ = entries[name]
        rows.append([name, digest(data), str(len(data))])
    rows.append([record, "", ""])
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    entries[record] = (stream.getvalue().encode(), 0o100644 << 16)

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(entries):
            data, attrs = entries[name]
            info = zipfile.ZipInfo(name, (2026, 10, 22, 0, 0, 0))
            info.create_system = 3
            info.external_attr = attrs
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    targets = (
        ("cp312", "os390_29_00_8561"),
        ("cp313", "os390_29_00_8561"),
        ("cp314", "zos"),
    )
    for python_tag, platform in targets:
        output = args.output_dir / (
            f"ruff-0.17.2-{python_tag}-none-{platform}.whl"
        )
        build(args.source, args.binary, output, python_tag, platform)
        print(output)


if __name__ == "__main__":
    main()
