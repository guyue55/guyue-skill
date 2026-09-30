#!/usr/bin/env python3
"""Prepare a Markdown document and local-image insertion plan for Feishu Docx."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path
from urllib.parse import unquote


DIRECT_IMAGE_RE = re.compile(
    r"^\s*!\[(?P<alt>[^\]]*)\]\((?P<target>[^)]+)\)\s*$"
)
LINKED_IMAGE_RE = re.compile(
    r"^\s*\[!\[(?P<alt>[^\]]*)\]\((?P<target>[^)]+)\)\]\([^)]+\)\s*$"
)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<text>.+?)\s*$")
LOCAL_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\((?P<target>[^)]+)\)")


def clean_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        return unquote(target[1:-1])
    if " " in target:
        target = target.split(" ", 1)[0]
    return unquote(target)


def plain_text(markdown_line: str) -> str:
    text = markdown_line.strip()
    if len(text) >= 2 and text[0] == text[-1] == "*":
        text = text[1:-1].strip()
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text)
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def selection_text(text: str, edge: int = 18) -> str:
    if len(text) <= edge * 2 + 3:
        return text
    return f"{text[:edge]}...{text[-edge:]}"


def find_anchor(lines: list[str], index: int) -> tuple[str, str]:
    for candidate in lines[index + 1 :]:
        if not candidate.strip():
            continue
        if HEADING_RE.match(candidate):
            break
        text = plain_text(candidate)
        if text:
            return text, "before"
        break

    for candidate in reversed(lines[:index]):
        if not candidate.strip():
            continue
        match = HEADING_RE.match(candidate)
        if match:
            return plain_text(match.group("text")), "after"

    return "", ""


def jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    offset = 2
    while offset + 9 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in {0xD8, 0xD9}:
            continue
        if offset + 2 > len(data):
            return None
        segment_length = struct.unpack(">H", data[offset : offset + 2])[0]
        if marker in {
            0xC0,
            0xC1,
            0xC2,
            0xC3,
            0xC5,
            0xC6,
            0xC7,
            0xC9,
            0xCA,
            0xCB,
            0xCD,
            0xCE,
            0xCF,
        }:
            height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
            return width, height
        offset += segment_length
    return None


def webp_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    payload = data[20:]
    if chunk == b"VP8X" and len(payload) >= 10:
        width = 1 + int.from_bytes(payload[4:7], "little")
        height = 1 + int.from_bytes(payload[7:10], "little")
        return width, height
    if chunk == b"VP8L" and len(payload) >= 5 and payload[0] == 0x2F:
        bits = int.from_bytes(payload[1:5], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8 ":
        start = payload.find(b"\x9d\x01\x2a")
        if start >= 0 and start + 7 <= len(payload):
            width, height = struct.unpack("<HH", payload[start + 3 : start + 7])
            return width & 0x3FFF, height & 0x3FFF
    return None


def image_dimensions(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data[:6] in {b"GIF87a", b"GIF89a"} and len(data) >= 10:
        return struct.unpack("<HH", data[6:10])
    return jpeg_dimensions(data) or webp_dimensions(data)


def local_path(target: str, source_dir: Path) -> Path | None:
    if target.startswith(("http://", "https://", "data:")):
        return None
    if target.startswith("file://"):
        return Path(target.removeprefix("file://")).expanduser().resolve()
    return (source_dir / target).expanduser().resolve()


def build_plan(source: Path, output_dir: Path, display_width: int) -> dict[str, object]:
    text = source.read_text(encoding="utf-8")
    lines = text.splitlines()
    output_lines: list[str] = []
    images: list[dict[str, object]] = []
    warnings: list[str] = []
    cwd = Path.cwd().resolve()

    for index, line in enumerate(lines):
        match = LINKED_IMAGE_RE.match(line) or DIRECT_IMAGE_RE.match(line)
        if not match:
            output_lines.append(line)
            continue

        target = clean_target(match.group("target"))
        resolved = local_path(target, source.parent)
        if resolved is None:
            output_lines.append(line)
            continue
        if not resolved.is_file():
            warnings.append(f"missing image: {target}")
            continue

        anchor, position = find_anchor(lines, index)
        if not anchor:
            warnings.append(f"no insertion anchor for image: {target}")
            continue

        dimensions = image_dimensions(resolved)
        if dimensions is None:
            warnings.append(f"unsupported image dimensions: {target}")
            continue
        width, height = dimensions
        target_width = min(display_width, width)
        target_height = max(1, round(height * target_width / width))
        try:
            cli_file = resolved.relative_to(cwd).as_posix()
        except ValueError:
            cli_file = ""
            warnings.append(
                f"image is outside current working directory; lark-cli needs a relative path: {resolved}"
            )

        images.append(
            {
                "source": target,
                "resolved_path": str(resolved),
                "cli_file": cli_file,
                "alt": match.group("alt").strip(),
                "selection": selection_text(anchor),
                "anchor_text": anchor,
                "position": position,
                "intrinsic_width": width,
                "intrinsic_height": height,
                "display_width": target_width,
                "display_height": target_height,
            }
        )

    cleaned = "\n".join(output_lines).rstrip() + "\n"
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    local_links = []
    for match in LOCAL_LINK_RE.finditer(cleaned):
        target = clean_target(match.group("target"))
        if not target.startswith(("http://", "https://", "#", "mailto:")):
            local_links.append(target)
    if local_links:
        warnings.append(
            "local-only links require review before online publication: "
            + ", ".join(sorted(set(local_links)))
        )

    selections = [str(item["selection"]) for item in images]
    duplicates = sorted({item for item in selections if selections.count(item) > 1})
    if duplicates:
        warnings.append(
            "duplicate media selections require manual disambiguation: "
            + ", ".join(duplicates)
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    document_path = output_dir / "document.md"
    plan_path = output_dir / "media-plan.json"
    document_path.write_text(cleaned, encoding="utf-8")

    result: dict[str, object] = {
        "source_markdown": str(source.resolve()),
        "prepared_markdown": str(document_path.resolve()),
        "image_count": len(images),
        "images": images,
        "warnings": warnings,
    }
    plan_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare Markdown and a local-image insertion plan for Feishu Docx."
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--display-width", type=int, default=800)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.display_width <= 0:
        raise SystemExit("--display-width must be positive")
    source = args.source.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"source Markdown not found: {source}")

    result = build_plan(source, args.output_dir, args.display_width)
    print(
        json.dumps(
            {
                "prepared_markdown": result["prepared_markdown"],
                "image_count": result["image_count"],
                "warning_count": len(result["warnings"]),
                "warnings": result["warnings"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if any(
        str(item).startswith(("missing image:", "no insertion anchor:", "unsupported image"))
        for item in result["warnings"]
    ) else 0


if __name__ == "__main__":
    sys.exit(main())
