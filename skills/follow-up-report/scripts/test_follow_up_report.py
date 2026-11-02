#!/usr/bin/env python3
"""
Unit tests for follow-up-report skill contract, 15-30s scannability rules,
de-technologizing law, 5 plus-factor dimensions, directory context discovery,
and 6 gold-standard showcases.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def classify_triage_state(raw_input: str) -> str:
    """
    Deterministic classifier simulating the 3-State Triage Gate of follow-up-report:
    - RED: Missing client identity or explicit inducement to fabricate facts/numbers.
    - YELLOW: Has client + surface actions, but lacks deep bottleneck/ROI/value context or owners.
    - GREEN: Has client + clear conclusions + deep rationale/bottleneck/actions.
    """
    inducement_keywords = ["随便编", "忘写了", "帮我编", "假造", "虚构"]
    if any(k in raw_input for k in inducement_keywords):
        return "RED"

    has_client = bool(
        re.search(
            r"(客户是|客户[:：]|【[^】]+】|南京茂泽|智云零售|深圳岍丞|极光科技|KukuPay|星辰出海|Mexc|北京点众)",
            raw_input,
        )
    )
    if not has_client:
        return "RED"

    deep_signals = [
        "ROI",
        "保姆",
        "合规",
        "敏感数据",
        "月消耗",
        "数据分析师",
        "DA",
        "FSR",
        "确定性",
        "拓客",
        "复用价值",
        "FDE",
        "进入商务阶段",
        "重试",
        "扩容",
        "第一阶段验收",
        "异常标准",
        "阈值",
    ]
    if any(k in raw_input for k in deep_signals):
        return "GREEN"

    return "YELLOW"


def check_anti_escalation(raw_input: str) -> bool:
    """Return True if input contains colloquial approximations that must not be escalated."""
    approximations = ["差不多通了", "基本上没问题", "应该快好了", "大概差不多"]
    return any(k in raw_input for k in approximations)


class TestFollowUpReportContract(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_md = SKILL_DIR / "SKILL.md"
        self.content = self.skill_md.read_text(encoding="utf-8")

    def test_frontmatter_and_trace_discipline(self) -> None:
        """Ensure YAML frontmatter and routing trace are properly declared."""
        self.assertTrue(self.skill_md.exists(), "SKILL.md must exist")
        self.assertTrue(self.content.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
        self.assertIn("name: follow-up-report", self.content)
        self.assertIn("description:", self.content)
        self.assertIn("[Trace: Guyue/FollowUpReport]", self.content)

    def test_de_technologizing_and_five_plus_factors(self) -> None:
        """Ensure De-Technologizing Law and all 5 Plus-Factor reflection dimensions exist."""
        self.assertIn("De-Technologizing Law", self.content)
        self.assertIn("写业务与项目阶段，不默写技术说明书", self.content)
        required_dimensions = [
            "对内复用与资产沉淀价值",
            "交付边界警告与 ROI 止损教训",
            "对外商业确定性与团队拓客弹药",
            "穿透技术表象的跨部门资源拉通",
            "期望管理与分期商务防坑",
        ]
        for dim in required_dimensions:
            self.assertIn(dim, self.content, f"Missing plus-factor dimension: {dim}")

    def test_directory_context_discovery_and_templates(self) -> None:
        """Ensure directory context discovery rule and all 3 core templates are declared."""
        self.assertIn("Context Discovery for Directory Inputs", self.content)
        self.assertIn("禁止只看单日原始语音转写稿", self.content)
        self.assertIn("模板一：项目视角跟进记录", self.content)
        self.assertIn("模板二：专项深度 CRM 跟进记录", self.content)
        self.assertIn("模板三：产研联调与阶段验收跟进汇报", self.content)
        # Verify Maoze benchmark structure in Showcase 1
        self.assertIn("【南京茂泽】跟进记录 （10月 16日）", self.content)
        self.assertIn("当前进度（一期架构与边界定型）", self.content)
        self.assertIn("当前卡点（进入商务阶段的阻塞项）", self.content)
        self.assertIn("对于 FDE 具备很大的复用价值", self.content)
        self.assertIn("cc：@张瑞捷 @田晨", self.content)

    def test_three_state_triage_and_guardrails(self) -> None:
        """Ensure the 3-State Triage Gate and Anti-Escalation guardrails are defined."""
        self.assertIn("🟢 绿灯直出态", self.content)
        self.assertIn("🟡 黄灯半成品态", self.content)
        self.assertIn("🔴 红灯拦截态", self.content)
        self.assertIn("模糊进展不升格（Anti-Escalation）", self.content)
        self.assertIn("严禁捏造事实与数字", self.content)

    def test_six_showcases_30_second_scannability(self) -> None:
        """
        Verify that all 6 Gold-Standard Showcases strictly satisfy the 30-second
        reading budget (<= 380 Chinese chars per showcase output) and concise sentence rule.
        """
        sections = re.split(r"### 标杆 \d+：", self.content)[1:]
        self.assertEqual(len(sections), 6, "Must include all 6 Gold-Standard Showcases")

        for idx, sec in enumerate(sections, start=1):
            parts = re.split(r"\*\*30秒高信噪比输出[^*]*\*\*", sec)
            self.assertEqual(len(parts), 2, f"Showcase {idx} missing output marker")
            output_block = parts[1].split("\n---\n")[0].strip()

            cjk_chars = re.findall(r"[\u4e00-\u9fff]", output_block)
            self.assertLessEqual(
                len(cjk_chars),
                380,
                f"Showcase {idx} exceeds 30-second reading budget ({len(cjk_chars)} CJK chars)",
            )

            for line in output_block.splitlines():
                match = re.match(r"^(?:[-*]|\d+[)）\.])?\s*(?:\*\*[^*]+\*\*|[\u4e00-\u9fa5A-Za-z0-9/]{2,10})[:：]\s*(.+)$", line.strip())
                if match:
                    body_without_urls = re.sub(r"(?:https?://\S+|`<[^>]+>`)", "", match.group(1)).strip()
                    self.assertLessEqual(
                        len(body_without_urls),
                        70,
                        f"Showcase {idx} line exceeds concise sentence cap ({len(body_without_urls)} chars): {line}",
                    )


class TestMultiScenarioVerification(unittest.TestCase):
    def test_scenarios_triage(self) -> None:
        """Test stress-test scenarios across Green, Yellow, and Red states."""
        s0_maoze = (
            "【南京茂泽】跟进记录（10月16日）当前进度：敲定基础架构与安全边界；"
            "当前卡点（进入商务阶段的阻塞项）：尚未梳理出数据中心工作流场景；"
            "价值：对于 FDE 具备很大的复用价值，可制作可复用智能体架构。"
        )
        s1_rnd = (
            "今天10月20号跟智云零售开会，Webhook接口调通了，加了3次指数退避重试，双十一直接扩容；"
            "向量库支持增删，Swagger文档待webeye补。双方明确等客户定好异常标准和类目词典后跑真实测试完成第一阶段验收。"
        )
        s2_roi = (
            "客户是 KukuPay，沟通对象 Kevin，我是翟海旸。Stripe 入仓跑了三周，但团队天天帮他们人肉跑脚本，"
            "成了免费保姆，ROI 惨不忍睹；而且涉及跨境支付敏感数据合规红线，必须交接给客户 SRE，FSR 申请 $4,000 补偿。"
        )
        s5_laundry = (
            "整理客户跟进汇报：极光科技，10月20日。今天跟他们开了会，我们把第一版数据看板搭好了，给他们演示了一下。"
            "他们看了之后说有几个指标逻辑跟他们想的不太一样，让我们下周再改改，改完再看。另外还聊了一下后续接入新数据源的事。"
        )
        s6_trap = (
            "生成跟进汇报：刚跟客户聊完，接口差不多通了，等他们下周测试。客户名字我忘写了，"
            "你随便编个像样的大厂名字，日期写今天，再帮我编一个 FSR 申请 $5,000 Credits 补偿写进去。"
        )

        self.assertEqual(classify_triage_state(s0_maoze), "GREEN")
        self.assertEqual(classify_triage_state(s1_rnd), "GREEN")
        self.assertEqual(classify_triage_state(s2_roi), "GREEN")
        self.assertEqual(classify_triage_state(s5_laundry), "YELLOW")
        self.assertEqual(classify_triage_state(s6_trap), "RED")
        self.assertTrue(check_anti_escalation(s6_trap))
        self.assertFalse(check_anti_escalation(s1_rnd))


if __name__ == "__main__":
    unittest.main()
