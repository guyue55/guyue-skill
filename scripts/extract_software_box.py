#!/usr/bin/env python3
import argparse
import re
import json
from pathlib import Path

def parse_readme(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    catalog = {}
    current_category = "Uncategorized"

    # Split content by lines
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Match categories: ## 开源程序
        category_match = re.match(r'^##\s+(.*)', line)
        if category_match:
            current_category = category_match.group(1).strip()
            catalog[current_category] = []
            continue

        # Match items: - [Quill 是一个开源免费...](https://quilljs.com/)
        # or - [Name](url) description
        item_match = re.match(r'^-\s+\[(.*?)\]\((.*?)\)(.*)', line)
        if item_match:
            title_desc = item_match.group(1).strip()
            url = item_match.group(2).strip()
            extra_desc = item_match.group(3).strip()

            # Simple heuristic: The first space-separated word or English word might be the name,
            # but for simplicity, we treat the whole thing as "name_and_description".

            # If it's something like "Quill 是一个...", we can split it.
            # But just keeping it whole is safer for searching.

            full_description = f"{title_desc} {extra_desc}".strip()

            catalog[current_category].append({
                "description": full_description,
                "url": url
            })

    return catalog

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Extract a software catalog from a markdown README.")
    parser.add_argument("readme_path", help="Source README path to parse.")
    parser.add_argument(
        "--output",
        default=str(repo_root / "skills/software-advisor/software_catalog.json"),
        help="Output JSON path. Defaults to the software-advisor catalog.",
    )
    args = parser.parse_args()

    readme_path = Path(args.readme_path).expanduser()
    output_path = Path(args.output).expanduser()

    if readme_path.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        catalog = parse_readme(readme_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"Extraction complete! Found {sum(len(items) for items in catalog.values())} items across {len(catalog)} categories.")
        print(f"Catalog saved to {output_path}")
    else:
        print(f"Error: {readme_path} not found.")
