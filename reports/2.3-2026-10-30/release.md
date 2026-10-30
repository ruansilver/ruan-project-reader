# 2.3 正式交付记录

日期：2026-10-30（Asia/Singapore）。用户已明确确认本次 2.3 为正式版本，并授权推送远端。按仓库三段版本号约定，目标版本、源码与正式成品统一为 **2.3.0**，对外名称为 **2.3**。

**正式交付不代表补丁全部验收通过：Goal 范围与恢复仍为 UNVERIFIED。** 本次按用户决定交付当前实现；没有把普通代理的暂停结果当成真实 Goal 调度证据。

## 文件与差异

- [首次修复报告](report.md) 保留初始版本、修改前映射、12 个修改文件、逐项验收与原始证据。其 install 2.2.0 和无 Git 元数据的记录属于首次修复阶段。
- [最终源码差异](final-source.diff) 对比保存的 2.2.0 源码与本次正式源码，包含全部 12 个修改文件，以及发布清单前后变化；原 [changes.diff](changes.diff) 保留首次修复阶段的版本标识 2.3。
- 正式登记新增 `design/versions/2.3.0.md`，记录用户确认、规范引用和验收边界；2.2 原稿、2.3 补丁原稿均未修改。
- 本轮将 `SKILL.md` 和检查器中已有的版本标识从 2.3 规范为 2.3.0；行为规则与首次修复后保持一致。
- `README.md`、`src/tests/README.md` 更新正式版本、安装位置、测试与限制；本目录的报告、校验日志及差异独立于 Skill。
- `install/ruan-project-reader/` 的 14 个文件从开发源构建，`install/.release.json` 由构建器生成；`install/ruan-project-reader.zip` 从校验后的安装目录打包。安装成品不包含测试、临时文件或报告。

远端原先只有工程骨架，尚无实际设计、源码、测试与成品。本次同步还会把本地既有工程材料纳入远端历史；这些既有材料不能全部归因于本次补丁修改。完整推送差异可在对应 Git 提交中核对。

## 验证结果

| 检查 | 结果 | 证据与范围 |
| --- | --- | --- |
| 原有测试及新增回归 | PASS | [构建日志](release-build.txt)：36 项测试全部通过；原 35 项测试保留 |
| 源码 Skill 结构 | PASS | 首次结构校验通过，正式版本规范后再次校验通过；仅覆盖 Skill 格式 |
| 正式安装 Skill 结构 | PASS | [安装校验](install-validation.txt) |
| 构建及发布一致性 | PASS | [构建日志](release-build.txt)、[发布校验](release-verify.txt)：目标、源码、成品及规定哈希一致 |
| 正式检查器执行 | PASS | [安装检查器日志](install-check.txt)：实际运行既有 valid-map 夹具；仅证明支持的机械契约 |
| ZIP 完整性 | PASS | [发布校验数据](release-validation.json)：解包条目与安装目录的 14 个文件逐一相同，压缩文件校验通过 |
| 总览与下研、两次人工接力、完成闸门、未读入口、逐条待办、最小回归 | PASS | [验收报告](report.md) 列出隔离样例、模拟输入、结果与有限覆盖范围 |
| Goal 范围与恢复 | UNVERIFIED | 未运行真实 Goal 自动循环，不能宣称 2.3 已完成全部验收 |
| Claude Code、DeepSeek Harness、Windows 的实际加载和全流程 | UNVERIFIED | 当前只核验标准目录、相对路径与本地 Python 执行；没有跨平台实测 |

模拟接力样例的机械检查有 6 项 UNVERIFIED，原始输出与原因保留在首次报告中。真实远端往返、长期恢复和 Mermaid 完整渲染亦未验证。

提交前全量 `git diff --cached --check` 返回 2：旧设计的 Markdown 换行空格、原始带行号摘录，以及 `.diff` 中的空白上下文被报告为尾随空格。这些原始材料保持原样。限定正式源码、安装目录、本轮登记、测试变更和发布说明的检查返回 0。

## 正式成品

| 项目 | 值 |
| --- | --- |
| 目标／已发布工程版本 | 2.3.0 |
| 设计 | `design/versions/2.3.0.md` |
| 安装目录 | `install/ruan-project-reader/` |
| 安装包 | `install/ruan-project-reader.zip` |
| design_sha256 | `fa1cf28cec6d6af64ab9338067077c35312abd0f1c6502f430bea58f30adc21f` |
| artifact_sha256 | `a5ff4d6805b00391e6bd68b7e669692325882a0d189ebab33545f67ac08e3cce` |
| ZIP SHA-256 | `038ebe40931480287c17e7da401b9c82edaaa2cf57e65540e9ede98948d30754` |

## Git 同步依据

仓库：[ruansilver/ruan-project-reader](https://github.com/ruansilver/ruan-project-reader)，分支 `main`。同步基点为 `08fd5deff8df81952b75f1a94d3222e9822a2b7d`。

本地最初缺少 `.git`，已读取远端骨架并恢复相同历史作为基点，保留本地文件；随后以普通提交和非强制推送同步。`src/.work/description/` 是既有忽略内容，继续保留且不纳入提交。此记录随正式内容提交，具体提交编号和推送确认以最终交付消息及远端 Git 历史为准。
