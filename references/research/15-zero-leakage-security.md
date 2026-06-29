# 15. Zero-Leakage 安全与代码洁癖 (Security & Anti-Bloat)

本研究档案记录了关于“Zero-Leakage (绝对防泄密)”与代码洁癖的深入打磨理念。这是古月大盘心法中至关重要的一环。

## 背景与痛点

在 AI 辅助编程与数字孪生演进的过程中，极容易发生两类泄漏事故：
1. **隐私与敏感信息泄漏**：代码库无意中包含 `sk-ant-`, `sk-proj-`, `API_KEY` 等认证密钥，或者包含开发者本机的绝对路径（例如 `/Users/xxx/...`）。一旦推送远端，将导致凭据被盗刷的严重安全事故。
2. **代码脂肪泄漏 (Anti-Lindy/Anti-Permacomputing)**：随手一交，把 `__pycache__/`, `*.pyc`, `.DS_Store`, 甚至 `.idea/` 这些二进制死脂肪统统抛入 Git 历史。久而久之，历史仓库变得极其臃肿，严重拖慢 Agent 检索效率，违背了极简的永续计算原则。

## 解决思路：物理防线拦截 (The Security Scanner)

我们坚信，“口头纪律不如物理拦截”。

### 1. 强制 Git 黑名单
所有的临时文件夹、缓存与私人笔记，必须在 `.gitignore` 层面根除。
```gitignore
# Python
__pycache__/
*.py[cod]

# Personal
references/sources/
references/research/*
!references/research/14-permacomputing-lindy.md
!references/research/15-zero-leakage-security.md
```

### 2. CI 级拦截门神 (`security_scanner.py`)
在最外层的 `test_suite.sh` 中，我们挂载了 `security_scanner.py`。
- **职责**：遍历 `git ls-files` 中追踪的所有文件。
- **嗅探**：正则嗅探泄漏特征码。
- **阻断**：一旦扫描到危险特征码或冗余二进制脂肪，强制 `exit(1)` 并报警阻断提交流程。

### 3. Git 历史洗底 (History Scrubbing)
如果已经不小心提交了敏感信息，单纯的 `git rm` 或 `.gitignore` 是无效的（因为它们依然躺在历史 commit 的快照中）。
必须使用 `git filter-branch` 或 `git filter-repo` 将其从历史树中彻底物理切除，然后 `git push --force` 强行覆盖远程。

## 结论
Zero-Leakage 是保持架构健康、让系统活得更久的红线。没有安全与代码洁癖的加持，再先进的架构也只是一团岌岌可危的毛线球。
