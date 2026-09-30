#!/usr/bin/env python3
"""
Unit tests for work-pulse-distiller skill contract, heuristics, and formatting.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
SKILL_DIR = Path(__file__).resolve().parent.parent


class TestWorkPulseDistillerContract(unittest.TestCase):
    def setUp(self):
        self.skill_md = SKILL_DIR / "SKILL.md"
        self.classification_md = SKILL_DIR / "references" / "classification-and-heuristics.md"
        self.templates_md = SKILL_DIR / "references" / "templates-and-examples.md"

    def test_skill_files_exist(self):
        """Ensure all standard skill files exist."""
        self.assertTrue(self.skill_md.exists(), "SKILL.md must exist")
        self.assertTrue(self.classification_md.exists(), "classification-and-heuristics.md must exist")
        self.assertTrue(self.templates_md.exists(), "templates-and-examples.md must exist")

    def test_frontmatter_and_trace(self):
        """Ensure YAML frontmatter is valid and required trace discipline is declared."""
        content = self.skill_md.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
        self.assertIn("name: work-pulse-distiller", content)
        self.assertIn("description:", content)
        self.assertIn("[Trace: Guyue/WorkPulseDistiller]", content)

    def test_two_tier_contract_declared(self):
        """Ensure the two-tier structure is explicitly declared."""
        content = self.skill_md.read_text(encoding="utf-8")
        self.assertIn("📊 本周工作周报", content)
        self.assertIn("📈 项目精简进度汇报", content)
        self.assertIn("本周进展：", content)
        self.assertIn("下周计划：", content)
        self.assertIn("🟢", content)
        self.assertIn("🟡", content)
        self.assertIn("🔴", content)

    def test_anti_patterns_and_patching(self):
        """Ensure anti-patterns and incremental patching are defined."""
        content = self.skill_md.read_text(encoding="utf-8")
        self.assertIn("否定清单", content)
        self.assertIn("增量补充", content)


class TestDistillationLogic(unittest.TestCase):
    def test_sample_raw_logs_aggregation(self):
        """Simulate distillation of fragmented raw logs."""
        raw_logs = [
            "1. FlowOps-工单系统: 已部署到 Cloud Run，解决部署异常 5+ 项: https://flowops-app.run.app",
            "2. AI 视频平台Demo: 首页优化，重构模型配置",
            "3. 自动化创建云资源项目: 新需求开发完成，测试中",
            "补充: FlowOps 飞书机器人问答已打通，并优化了 RAG 参数",
        ]

        # Extract links
        links = []
        for log in raw_logs:
            found = re.findall(r"https?://[^\s]+", log)
            links.extend(found)
        self.assertEqual(len(links), 1)
        self.assertIn("https://flowops-app.run.app", links)

        # Entity identification
        entities = {"FlowOps": [], "VideoStudio": [], "云自动化工具": []}
        for log in raw_logs:
            if "FlowOps" in log or "工单系统" in log:
                entities["FlowOps"].append(log)
            elif "AI 视频" in log or "VideoStudio" in log:
                entities["VideoStudio"].append(log)
            elif "云资源" in log or "云自动化" in log:
                entities["云自动化工具"].append(log)

        self.assertEqual(len(entities["FlowOps"]), 2)
        self.assertEqual(len(entities["VideoStudio"]), 1)
        self.assertEqual(len(entities["云自动化工具"]), 1)

    def test_status_heuristics(self):
        """Test status color assignment heuristics."""
        def evaluate_status(text: str) -> str:
            if any(k in text for k in ["阻塞", "卡死", "失败", "报错", "被拦截", "严重异常"]):
                return "🔴"
            if any(k in text for k in ["测试中", "方案设计", "沟通中", "待定", "推进中", "评估中", "调研"]):
                return "🟡"
            return "🟢"

        self.assertEqual(evaluate_status("系统已上线，完成重构部署并解决 5+ 异常"), "🟢")
        self.assertEqual(evaluate_status("新需求开发完成，测试中"), "🟡")
        self.assertEqual(evaluate_status("SiteAuditor 诊断失败，被拦截无法采集"), "🔴")


if __name__ == "__main__":
    unittest.main()
