#!/usr/bin/env python3
import sys
from pathlib import Path

RED_PATTERNS = [
    "ignore previous instructions",
    "curl -s",
    "| bash",
    "rm -rf",
    "os.system(",
    "subprocess.run(",
    "password=",
    "token=",
    "api_key=",
]

YELLOW_PATTERNS = [
    "http://",
    "https://",
    "chmod +x",
    "eval(",
    "exec(",
    "open(",
]

def run_scan(target_path):
    print(f"[Trace: Guyue/SecurityGate] 启动本地启发式预检，扫描目标: {target_path} ...")

    path = Path(target_path).expanduser()
    if not path.exists():
        return {
            "status": "Yellow",
            "findings": [
                {"type": "Manual Review", "severity": "Medium", "desc": "目标不是本地可读路径；仅能记录来源，不能宣称已完成代码扫描"}
            ],
        }

    files = [path] if path.is_file() else [
        p for p in path.rglob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".py", ".sh", ".js", ".ts", ".json", ".yaml", ".yml"}
    ]

    findings = []
    for file_path in files[:200]:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError as exc:
            findings.append({"type": "Read Error", "severity": "Low", "desc": f"{file_path}: {exc}"})
            continue

        for pattern in RED_PATTERNS:
            if pattern in content:
                findings.append({"type": "Red Flag Pattern", "severity": "Critical", "desc": f"{file_path}: contains `{pattern}`"})
        for pattern in YELLOW_PATTERNS:
            if pattern in content:
                findings.append({"type": "Sensitive Pattern", "severity": "Medium", "desc": f"{file_path}: contains `{pattern}`"})

    if any(item["severity"] == "Critical" for item in findings):
        return {"status": "Red", "findings": findings}
    if findings:
        return {"status": "Yellow", "findings": findings}
    return {"status": "Green", "findings": []}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_security_scan.py <target_path>")
        sys.exit(1)

    target = sys.argv[1]
    result = run_scan(target)

    print("\n" + "="*40)
    print(f"🛡️ 安全检查报告 (Local Heuristic Preflight)")
    print("="*40)

    if result["status"] == "Green":
        print("✅ 状态: Green (安全放行)")
        print("说明: 未发现任何已知的高危代码注入或越权行为。")
    elif result["status"] == "Yellow":
        print("⚠️ 状态: Yellow (敏感告警)")
        for f in result["findings"]:
            print(f" - [{f['severity']}] {f['type']}: {f['desc']}")
        print("建议: 需人工确认授权后方可执行。")
    elif result["status"] == "Red":
        print("❌ 状态: Red (致命拦截)")
        for f in result["findings"]:
            print(f" - [{f['severity']}] {f['type']}: {f['desc']}")
        print("建议: 存在红旗指标，严禁挂载！")
    else:
        print("❓ 状态: Error (扫描失败)")
