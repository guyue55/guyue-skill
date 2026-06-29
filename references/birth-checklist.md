# 鲁班工坊发版协议 (Birth Checklist)

> “真实无遗漏，一一阅读处理”

在任何版本的古月数字孪生正式 Release 前，必须执行并勾选以下所有工业级 SOP 检查项。

## 1. 架构级核查
- [x] 所有 `SKILL.md` 是否都已注入最新的底层心智（当前核心：Permacomputing & Lindy Effect）？
- [x] 是否存在没有被任何模块调用的“僵尸死代码”（Dead Code）？
- [x] `skills_manifest.json` 与 `README.md` 中的版本号是否已同步 Bump？

## 2. CI/CD 与语法探针
- [x] 运行 `python3 -m py_compile scripts/*.py`，是否有语法错误？
- [x] 运行 `scripts/test_suite.sh`，探针与 CI 断言是否 100% 绿灯？
- [x] 是否已使用 `grep_search` 全局排查硬编码绝对路径（如 `/Users/xxx`）？

## 3. 测试与文档
- [x] `test-prompts.json` 中的断言是否与最新引入的心智相匹配？
- [x] `README.md` 语法是否合法（没有未闭合的 Code Block 导致渲染破版）？

## 4. 发版仪式
- [x] 以上条件全部达成后，方可宣告发版成功并提交 Git 记录。
