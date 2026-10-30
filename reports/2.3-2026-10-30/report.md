# ruan-project-reader 2.3 修复与验收报告

日期：2026-10-30（Asia/Singapore）。本报告及证据独立于 `src/ruan-project-reader/`，不会进入安装成品。

本文保留首次修复阶段的实际验收记录：当时源码修复已落实，Goal 范围与恢复尚未验证，尚未发布。用户随后明确将 2.3 定为正式版本并授权推送，最新正式交付状态见 [release.md](release.md)。**正式交付不把 Goal 的 UNVERIFIED 改写为 PASS，也不宣称补丁全部验收通过。** 下文版本与 Git 状态均对应首次修复结束时。

## 基线、目标与发布状态

| 项目 | 实际结果 |
| --- | --- |
| 用户指定修复目标 | 2.3 补丁；仅更新实现中已有版本标识 |
| 维护约定选出的 approved 目标 | `design/versions/2.2.0.md`，版本 2.2.0；2.3 补丁在子目录中，没有标准 approved 版本登记 |
| 修改前源码／已发布版本 | 均为 2.2.0；源码与成品一致，设计与成品哈希校验通过 |
| 修改后源码 | SKILL metadata.version 与检查器已有版本标识为 2.3 |
| install | 保持 2.2.0，目录、发布清单和原 ZIP 均未修改；未执行构建 |
| Git | `git status --short` 返回 not a git repository；无法判断未提交差异，未初始化、提交、推送或打 Tag |
| 原有临时材料 | `src/.work/description/` 保留，本次证据直接保存在本报告目录 |

初始检查：[35 项测试结果](baseline-tests.txt)、[发布一致性](baseline-release.txt)、[原始文件哈希](before-sha256.json)。修改前已完整读取补丁、实际入口、全部引用资料与模板、检查器、现有两个测试文件及构建脚本；[逐项映射](mapping-before.md) 记录了规则缺失、规则冲突、已有正确实现及执行偏离的证据边界。

没有修改 2.2 原稿，也没有为了发布新建 approved 设计文件或改动版本选择／构建机制。2.3 正式发布需要先补足实际验收证据，并由用户决定其版本登记；本报告不把源码版本号当成发布凭据。

## 实际修改文件与前后 diff

完整独立差异：[changes.diff](changes.diff)。修改前文件在 [before/](before/)；[完整性记录](integrity.json) 列出所有 12 个既有文件的变化。除下列文件外，初始哈希清单内其他文件保持一致。

| 文件 | 实际变更 |
| --- | --- |
| `src/ruan-project-reader/SKILL.md` | 版本 2.3；每层下研后成文、首轮总览、范围、两次交接暂停、等待恢复及完成输入前提 |
| `references/modules.md` | 调查首段明确证据驱动的先下研后成文；原拆分、父子契约及叶子判据保留 |
| `references/discovery.md` | 首轮可审阅总览即交接；已发现入口立即登记，未展开有去向；允许主体流程尚未独立成文时定位总览节点 |
| `references/collaboration.md` | 本阶段范围、每次交接终止、Goal 终点与故障处理、等待恢复、已收到材料与补证定位 |
| `references/completion.md` | 本层完成要求用户转交质疑和完整稿，并核实源码及处理记录；缺输入保持梳理中 |
| `references/check-format.md` | 明确协作事实及其记录位置属于人工核验，不由 check 证明 |
| `templates/COVERAGE.md` | 入口未展开／未映射也登记并派生原始任务 |
| `templates/STATE.md` | 复用当前焦点与下一步填写对象、等待材料和恢复动作 |
| `templates/module.md` | 复用源码依据、核验与下一步段落填写下研证据及远端输入／处理位置 |
| `templates/remote-relay.md` | 首轮总览、范围与阶段交付物、交接后结束、收到输入的定位 |
| `scripts/check.py` | 两处既有版本标识改为 2.3；人工核验列表增加远端输入提示；检查逻辑未改 |
| `src/tests/test_check.py` | 保留原有测试；重复待办用例增加 1→0 及逐步断言，新增已知未展开入口登记测试 |

表中未带前缀的路径均相对 `src/ruan-project-reader/`。新增文件仅为本报告、修改前快照、隔离样例和验收证据；没有新增 Skill 资源、状态字段、数据库、通用调用图系统、固定深度规则、自动双 AI 通信或 Figma 任务。保留 Mermaid、短注、下钻链接和源码定位契约。

## 补丁第五节验收

PASS 只针对下表实际执行的有限场景。模型行为试用由 Skill Creator 指定的独立试用代理执行，读取修订后的 Skill 与原始隔离材料，不提供补丁或预期答案。模拟转交由维护者构造，**不是实际远端审查**。受控记录演练与自主模型行为分别标明。

| 用例 | 结果 | 实际证据 | 未验证范围 |
| --- | --- | --- | --- |
| 总览与向下预研 | PASS | [run-1](evidence/isolated/run-1.md)：先读到 routes→service→rules→policy 的深层开关与数量判断，再写总览；首次返回时仅一份模块，发现收敛为否、5 条未决仍保留；[首次快照](evidence/isolated/stage-1-map/modules/00-总览.md) 与 [转交代码块](evidence/isolated/relay-1.md) 可复核 | 六文件合成项目；未证明所有真实项目或任意深度表现 |
| 两次人工接力及范围 | PASS | [首次返回](evidence/isolated/run-1.md) 后结束；[无新输入重触发](evidence/isolated/run-2.md) 保持等待且 [文件哈希不变](evidence/isolated/resume-without-input.json)；收到 [模拟质疑 Q1](evidence/isolated/simulated-questions.md) 后才在 [run-3](evidence/isolated/run-3.md) 补证，并再次返回等待完整稿；收到 [模拟完整稿 F1](evidence/isolated/simulated-full-document.md) 后才在 [run-4](evidence/isolated/run-4.md) 核验保存。E4 只登记，始终仅总览一份模块；F1 接收后仅消解协作待办，6→5，其余缺口保留，状态仍梳理中 | Q1/F1 由维护者模拟；未验证真实远端质量、真实用户操作或 Goal 调度 |
| Goal 范围与恢复 | UNVERIFIED | 规则已写入 SKILL 与 collaboration；普通代理重触发确实保持等待，但本轮没有运行平台 Goal 自动循环 | Goal 到交接点自动终止、自动重触发及进程中断恢复均未实测；没有以手动中止或普通代理返回记作 PASS |
| 完成闸门 | PASS | [独立执行记录](evidence/completion-gate/result.md)：文件齐全、check 退出 0 且 292 项通过，仍因缺远端输入而不标完成；[检查原始 JSON](evidence/completion-gate/before-check.json)、[哈希核验](evidence/completion-gate/integrity.json) 证明知识库保持原状 | 一个负例；不能证明所有提示下均拒绝错误完成，也未进行真实远端审查 |
| 已知未读入口 | PASS | [Q1 中的额外源码摘录](evidence/isolated/simulated-questions.md) 给出 `/audit` 入口、未提供 AuditService 内部；[run-3](evidence/isolated/run-3.md) 将其登记为 E4，标“未展开／未映射”并保留下一步与原始限制；[交接快照](evidence/isolated/stage-3-map/COVERAGE.md) 记录入口 3→4、原始待办 5→6，仍只有总览模块。新增机械回归也实跑通过 | 已知摘录的有限场景；没有验证大仓库入口发现召回率 |
| 重复待办 | PASS | [受控源码演练结果](evidence/duplicate/results.json)：相同来源、同一目标的两行，先读并执行开关分支、只消解第一行，再读并执行数量分支消解第二行；三个快照 stage-2、stage-1、stage-0 和 check JSON 记录 2→1→0，均机械通过；既有测试也扩展实跑通过 | 这是维护者控制的逐条源码／记录演练；未把它称为模型自主选择待办的长期表现 |
| 最小无痕回归 | PASS | [修改后 36 项测试](after-tests.txt)、[Skill Creator 校验](skill-validation.txt)、[完整 diff](changes.diff)、[完整性核查](integrity.json)；原 35 项测试全部保留，其他 29 份既有测试／夹具文件哈希不变 | Skill 结构与有限回归不保证业务语义完整或跨平台自动调度行为 |

首轮模型样例的机械检查实际为退出 2：314 项通过、6 项未验证、0 项失败，完整输出在 [check-run-1.json](evidence/isolated/check-run-1.json)。四项未验证涉及扫描缺口到原始未决的支持格式关联，两项为由此产生的待办／阻塞派生未知。执行者保留人工核对的 5 条待办、0 条阻塞并明确自动值未知，未冒称机械全绿、未为过检新增重复任务。它与完成闸门用例中机械全绿的独立样例是两个不同测试。

第二次交接前 [check-run-3.json](evidence/isolated/check-run-3.json) 为 341 项通过、6 项未验证、0 失败；完整稿保存后的 [check-run-4.json](evidence/isolated/check-run-4.json) 为 332 项通过、6 项未验证、0 失败。输入与处理位置保存在总览现有“核验与下一步”段落；等待完整稿任务只在收到 F1 后消解。三个源码限制仍保留，本层没有被强行标为完成。这些实际未验证明细没有被验收表中的行为 PASS 遮盖。

## 未验证范围与剩余限制

- **关键未验证项：Goal。** 本轮未启用真实 Goal 自动续跑，普通代理终止和重新触发的证据不能替代 Goal 调度器证据，因此不宣称 2.3 完成验收。
- Claude Code、DeepSeek Harness、Windows 的实际安装和全流程均未测试。核心仍使用原有标准 Skill 目录、相对引用与 Python 标准库；不把文件可移植性当成平台实测。
- 真实远端 AI 参与、真实用户人工复制交接和长期项目恢复未验证。隔离接力中的远端输入均显式标为模拟。
- Mermaid 完整语法／渲染和真实运行宿主未验证；检查器继续只证明其支持的机械契约。原有未知传播和只读行为保持。
- 样例输入、快照与执行日志是验收证据，不进入正式 Skill，也不证明被阅读的真实项目已完整覆盖。
- 没有超出补丁范围修改原始设计、构建器或被阅读项目的功能代码。正式安装仍为原 2.2.0，不能把开发源当成已发布的 2.3 安装包。

## 可复核命令

在工程根目录执行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s src/tests -v
python3 src/ruan-project-reader/scripts/check.py reports/2.3-2026-10-30/evidence/completion-gate/project-map --json
```

修改后实际执行 `src/build_release.py --verify`，退出 1，提示“开发源的交付文件与成品不一致”，见 [日志](after-release-verify.txt)。这是预期的开发中／未发布状态；本次没有通过重新构建来掩盖差异。旧成品本身的 manifest 与规定哈希已单独复核，仍有效。没有执行发布、提交或推送。
