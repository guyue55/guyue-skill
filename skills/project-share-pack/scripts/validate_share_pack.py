#!/usr/bin/env python3
"""Validate the local artifact contract of a project sharing package."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from prepare_feishu_publish import (
    DIRECT_IMAGE_RE,
    LINKED_IMAGE_RE,
    clean_target,
    image_dimensions,
)


SLIDE_RE = re.compile(
    r"<section\b[^>]*\bclass=[\"'][^\"']*\bslide\b[^\"']*[\"']",
    re.IGNORECASE,
)
TITLE_RE = re.compile(r"<title\b[^>]*>(?P<title>.*?)</title>", re.IGNORECASE | re.DOTALL)
RESOURCE_PATTERNS = {
    "script": re.compile(r"<script\b[^>]*\bsrc=[\"'](?P<url>[^\"']+)", re.IGNORECASE),
    "stylesheet": re.compile(
        r"<link\b[^>]*\b(?:href=[\"'](?P<url1>[^\"']+)[\"'][^>]*\brel=[\"'][^\"']*stylesheet"
        r"|rel=[\"'][^\"']*stylesheet[^\"']*[\"'][^>]*\bhref=[\"'](?P<url2>[^\"']+))",
        re.IGNORECASE,
    ),
    "image": re.compile(r"<(?:img|source)\b[^>]*\bsrc=[\"'](?P<url>[^\"']+)", re.IGNORECASE),
    "media": re.compile(
        r"<(?:video|audio)\b[^>]*\b(?:src|poster)=[\"'](?P<url>[^\"']+)",
        re.IGNORECASE,
    ),
    "css": re.compile(r"url\(\s*[\"']?(?P<url>[^)'\"\s]+)", re.IGNORECASE),
}
SENSITIVE_PATTERNS = {
    "local file URL": re.compile(r"file://", re.IGNORECASE),
    "macOS user path": re.compile("/" + r"Users/[^/\s\"'<>]+/"),
    "Linux home path": re.compile("/" + r"home/[^/\s\"'<>]+/"),
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"'<>]+\\"),
    "credential-like assignment": re.compile(
        r"(?i)\b(?:access[_-]?token|api[_-]?key|client[_-]?secret|authorization)"
        r"\s*[:=]\s*[\"']?[A-Za-z0-9._~+/=-]{8,}"
    ),
}


def html_title(text: str) -> str:
    match = TITLE_RE.search(text)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group("title")).strip()


def portable_dependencies(text: str) -> list[dict[str, str]]:
    dependencies: list[dict[str, str]] = []
    for kind, pattern in RESOURCE_PATTERNS.items():
        for match in pattern.finditer(text):
            url = next((value for value in match.groupdict().values() if value), "")
            normalized = unquote(url.strip())
            if not normalized or normalized.startswith(("data:", "blob:", "#")):
                continue
            dependencies.append({"type": kind, "url": normalized[:240]})
    return dependencies


def markdown_images(document: Path) -> tuple[list[dict[str, object]], list[str]]:
    images: list[dict[str, object]] = []
    errors: list[str] = []
    for line_number, line in enumerate(
        document.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = LINKED_IMAGE_RE.match(line) or DIRECT_IMAGE_RE.match(line)
        if not match:
            continue
        target = clean_target(match.group("target"))
        if target.startswith(("http://", "https://", "data:")):
            images.append({"line": line_number, "source": target, "remote": True})
            continue
        path = (document.parent / target).resolve()
        if not path.is_file():
            errors.append(f"Markdown image is missing at line {line_number}: {target}")
            continue
        dimensions = image_dimensions(path)
        if dimensions is None:
            errors.append(
                f"Markdown image dimensions are unsupported at line {line_number}: {target}"
            )
            continue
        width, height = dimensions
        images.append(
            {
                "line": line_number,
                "source": target,
                "resolved_path": str(path),
                "remote": False,
                "width": width,
                "height": height,
            }
        )
    return images, errors


def forbidden_terms(args: argparse.Namespace) -> list[str]:
    terms = [item.strip() for item in getattr(args, "forbid_term", []) if item.strip()]
    terms_file = getattr(args, "forbid_terms_file", None)
    if terms_file:
        path = Path(terms_file).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"forbidden terms file not found: {path}")
        terms.extend(
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    return list(dict.fromkeys(terms))


def privacy_findings(
    artifacts: dict[str, str], custom_terms: list[str]
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for artifact, text in artifacts.items():
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                findings.append({"artifact": artifact, "rule": label})
        lowered = text.casefold()
        for index, term in enumerate(custom_terms, start=1):
            if term.casefold() in lowered:
                findings.append(
                    {"artifact": artifact, "rule": f"custom forbidden term #{index}"}
                )
    return findings


def validate(args: argparse.Namespace) -> dict[str, object]:
    document = args.document.expanduser().resolve()
    deck = args.deck.expanduser().resolve()
    portable = args.portable_deck.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for label, path in (
        ("document", document),
        ("deck", deck),
        ("portable deck", portable),
    ):
        if not path.is_file():
            errors.append(f"{label} not found: {path}")

    if errors:
        return {"status": "fail", "errors": errors, "warnings": warnings}

    images, image_errors = markdown_images(document)
    errors.extend(image_errors)
    local_images = [item for item in images if not item.get("remote")]
    remote_images = [item for item in images if item.get("remote")]
    if not images:
        warnings.append("The document contains no Markdown screenshots.")
    if remote_images:
        warnings.append(
            f"The document uses {len(remote_images)} remote image(s); online availability may drift."
        )
    small_images = [
        item
        for item in local_images
        if int(item.get("width", 0)) < args.min_image_width
    ]
    if small_images:
        warnings.append(
            f"{len(small_images)} local screenshot(s) are narrower than "
            f"{args.min_image_width}px."
        )

    deck_text = deck.read_text(encoding="utf-8")
    portable_text = portable.read_text(encoding="utf-8")
    document_text = document.read_text(encoding="utf-8")
    deck_title = html_title(deck_text)
    portable_title = html_title(portable_text)
    slide_count = len(SLIDE_RE.findall(deck_text))
    portable_slide_count = len(SLIDE_RE.findall(portable_text))

    if not deck_title:
        errors.append("The maintainable deck has no HTML title.")
    if not portable_title:
        errors.append("The portable deck has no HTML title.")
    if deck_title and portable_title and deck_title != portable_title:
        errors.append("The maintainable and portable deck titles do not match.")
    if slide_count < args.min_slides:
        errors.append(
            f"The maintainable deck has {slide_count} slide(s); "
            f"minimum is {args.min_slides}."
        )
    if portable_slide_count != slide_count:
        errors.append(
            f"Slide count differs: maintainable={slide_count}, portable={portable_slide_count}."
        )

    dependencies = portable_dependencies(portable_text)
    if dependencies:
        preview = ", ".join(
            f"{item['type']}:{item['url']}" for item in dependencies[:5]
        )
        errors.append(
            "The portable deck still depends on external or sibling resources: " + preview
        )

    try:
        custom_terms = forbidden_terms(args)
    except ValueError as exc:
        errors.append(str(exc))
        custom_terms = []
    findings = privacy_findings(
        {
            "document": document_text,
            "deck": deck_text,
            "portable deck": portable_text,
        },
        custom_terms,
    )
    if findings:
        summary = ", ".join(
            f"{item['artifact']}:{item['rule']}" for item in findings[:8]
        )
        errors.append("Potential customer or local information leakage: " + summary)

    return {
        "status": "pass" if not errors else "fail",
        "document": str(document),
        "deck": str(deck),
        "portable_deck": str(portable),
        "deck_title": deck_title,
        "slide_count": slide_count,
        "document_image_count": len(images),
        "portable_dependency_count": len(dependencies),
        "privacy_finding_count": len(findings),
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document", required=True, type=Path)
    parser.add_argument("--deck", required=True, type=Path)
    parser.add_argument("--portable-deck", required=True, type=Path)
    parser.add_argument("--min-slides", type=int, default=5)
    parser.add_argument("--min-image-width", type=int, default=1200)
    parser.add_argument(
        "--forbid-term",
        action="append",
        default=[],
        help="Customer-specific term that must not appear; may be repeated.",
    )
    parser.add_argument(
        "--forbid-terms-file",
        type=Path,
        help="Temporary newline-delimited denylist; do not store it in this Skill.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_slides <= 0 or args.min_image_width <= 0:
        raise SystemExit("minimum values must be positive")
    result = validate(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
