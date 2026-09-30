from __future__ import annotations

import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from test_prepare_feishu_publish import write_png
from validate_share_pack import validate


def deck_html(title: str, slides: int, resource: str = "") -> str:
    sections = "".join('<section class="slide">内容</section>' for _ in range(slides))
    return f"<!doctype html><html><head><title>{title}</title>{resource}</head><body>{sections}</body></html>"


class ValidateSharePackTest(unittest.TestCase):
    def test_accepts_complete_local_package(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            root = Path(temp)
            write_png(root / "overview.png", 1600, 900)
            document = root / "方案.md"
            document.write_text(
                "# 项目方案\n\n![完整概览](overview.png)\n\n*图 1：完整概览*\n",
                encoding="utf-8",
            )
            deck = root / "index.html"
            portable = root / "index-feishu.html"
            deck.write_text(deck_html("项目分享", 6), encoding="utf-8")
            portable.write_text(
                deck_html(
                    "项目分享",
                    6,
                    '<style>.hero{background:url("data:image/png;base64,AAAA")}</style>',
                ),
                encoding="utf-8",
            )

            result = validate(
                Namespace(
                    document=document,
                    deck=deck,
                    portable_deck=portable,
                    min_slides=5,
                    min_image_width=1200,
                    forbid_term=[],
                    forbid_terms_file=None,
                )
            )

            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["slide_count"], 6)
            self.assertEqual(result["document_image_count"], 1)
            self.assertEqual(result["portable_dependency_count"], 0)

    def test_rejects_external_portable_dependency(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            root = Path(temp)
            write_png(root / "overview.png", 1600, 900)
            document = root / "方案.md"
            document.write_text(
                "# 项目方案\n\n![概览](overview.png)\n",
                encoding="utf-8",
            )
            deck = root / "index.html"
            portable = root / "index-feishu.html"
            deck.write_text(deck_html("项目分享", 5), encoding="utf-8")
            portable.write_text(
                deck_html(
                    "项目分享",
                    5,
                    '<script src="./slides.js"></script>',
                ),
                encoding="utf-8",
            )

            result = validate(
                Namespace(
                    document=document,
                    deck=deck,
                    portable_deck=portable,
                    min_slides=5,
                    min_image_width=1200,
                    forbid_term=[],
                    forbid_terms_file=None,
                )
            )

            self.assertEqual(result["status"], "fail")
            self.assertEqual(result["portable_dependency_count"], 1)

    def test_rejects_customer_specific_term_without_echoing_it(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            root = Path(temp)
            write_png(root / "overview.png", 1600, 900)
            document = root / "方案.md"
            document.write_text(
                "# 示例方案\n\n![概览](overview.png)\n",
                encoding="utf-8",
            )
            deck = root / "index.html"
            portable = root / "index-feishu.html"
            deck.write_text(deck_html("示例分享", 5), encoding="utf-8")
            portable.write_text(
                deck_html("示例分享", 5).replace("内容", "PRIVATE_CLIENT"),
                encoding="utf-8",
            )

            result = validate(
                Namespace(
                    document=document,
                    deck=deck,
                    portable_deck=portable,
                    min_slides=5,
                    min_image_width=1200,
                    forbid_term=["PRIVATE_CLIENT"],
                    forbid_terms_file=None,
                )
            )

            self.assertEqual(result["status"], "fail")
            self.assertEqual(result["privacy_finding_count"], 1)
            self.assertNotIn("PRIVATE_CLIENT", " ".join(result["errors"]))


if __name__ == "__main__":
    unittest.main()
