from __future__ import annotations

import json
import sys
import struct
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from prepare_feishu_publish import build_plan


def write_png(path: Path, width: int = 1200, height: int = 600) -> None:
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + b"\x00\x00\x00\rIHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x06\x00\x00\x00"
    )


class PrepareFeishuPublishTest(unittest.TestCase):
    def test_builds_plan_for_image_with_caption(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            root = Path(temp)
            image = root / "report.png"
            write_png(image)
            source = root / "方案.md"
            source.write_text(
                "# 项目方案\n\n![报告概览](report.png)\n\n*图 1：报告概览*\n",
                encoding="utf-8",
            )

            result = build_plan(source, root / "out", 800)

            self.assertEqual(result["image_count"], 1)
            item = result["images"][0]
            self.assertEqual(item["anchor_text"], "图 1：报告概览")
            self.assertEqual(item["position"], "before")
            self.assertEqual(item["display_width"], 800)
            self.assertEqual(item["display_height"], 400)
            prepared = Path(result["prepared_markdown"]).read_text(encoding="utf-8")
            self.assertNotIn("report.png", prepared)

    def test_uses_previous_heading_before_next_section(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            root = Path(temp)
            write_png(root / "report.png")
            source = root / "方案.md"
            source.write_text(
                "# 项目方案\n\n## 报告示例\n\n![报告](report.png)\n\n## 边界\n",
                encoding="utf-8",
            )

            result = build_plan(source, root / "out", 800)

            item = result["images"][0]
            self.assertEqual(item["anchor_text"], "报告示例")
            self.assertEqual(item["position"], "after")

    def test_preserves_angle_wrapped_path_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
            root = Path(temp)
            write_png(root / "report overview.png")
            source = root / "方案.md"
            source.write_text(
                "# 项目方案\n\n![报告](<report overview.png>)\n\n*完整报告概览*\n",
                encoding="utf-8",
            )

            result = build_plan(source, root / "out", 800)

            self.assertEqual(result["image_count"], 1)
            self.assertEqual(result["images"][0]["source"], "report overview.png")
            plan = json.loads((root / "out" / "media-plan.json").read_text())
            self.assertEqual(plan["image_count"], 1)


if __name__ == "__main__":
    unittest.main()
