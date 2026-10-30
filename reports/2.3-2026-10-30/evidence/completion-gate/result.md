# 总览完成门禁：隔离合成试用

日期：2026-10-30。范围仅为本目录 `source/` 与 `project-map/`，使用指定开发源 Skill。这是隔离合成试用，不是真实项目分析，不证明其他项目或未提供材料的情况。

## 请求与结论

模拟请求：文档文件齐全且机械检查已全绿；复核 `project-map/modules/00-总览.md` 能否标为“本层完成”，满足时更新并核验；仅处理该总览。

结论：不能标为“本层完成”，保持原有“梳理中”。机械契约检查确实通过，但提供的全部材料没有本层远端质疑、用户实际转交的远端完整当前稿，以及本地逐项补证处理记录。现有总览文件本身不能证明其来自这套协作过程。

仅新增本试用记录；未修改 Skill、样例源码、总览、子模块、COVERAGE 或 STATE。没有调用 Goal、自动化、其他代理或外部消息，也没有读取设计、补丁、其他报告或代理材料。

## 实际读取

指定 Skill 根目录：`/mnt/ext_drive/workspace/AI workspace/skills/ruan-project-reader/src/ruan-project-reader/`。

- `SKILL.md`：完整读取，版本元数据为 2.3。
- `references/completion.md`：完整读取，核实完成前置条件、四项闸门及机械检查的证明范围。
- `references/check-format.md`：完整读取，核实计数口径、原始记录与人工核验边界。
- `references/collaboration.md`：完整读取，核实人工转交与协作事实要求。
- 执行 Skill 的 `scripts/check.py`；没有审读或修改其实现。

隔离材料根目录：本 `completion-gate/` 目录。

- `source/fixture.py`：完整读取，共一个 `save(value, rows)` 函数。
- `project-map/modules/00-总览.md`：完整读取，状态为梳理中，单节点 F 引用保存模块。
- `project-map/modules/保存.md`：只为核实总览引用边界完整读取；未展开新的模块工作。
- `project-map/COVERAGE.md`：完整读取，入口 E1、汇点 S1、三方向发现与一条交叉复查。
- `project-map/STATE.md`：完整读取，与机械派生计数对账。
- `project-map/README.md`：完整读取，其中明确写明只用于机械契约测试。

`rg --files` 在允许的 `source/` 与 `project-map/` 下列出上述 6 份材料；完整读取这些材料，并进一步使用关键词搜索核对协作记录，没有发现额外远端输入。

## 实际依据与人工判断

| 项目 | 实际证据 | 判断 |
| --- | --- | --- |
| 保存正常路径 | `source/fixture.py:1-3`：调用 `rows.append(value)` 后 `return value` | 可确认调用次序及正常返回值；不能据此推断数据库持久化或 rows 的具体类型 |
| 入口与总览映射 | `project-map/COVERAGE.md:12` 的 E1 指向保存模块与总览 F；总览短注引用 E1 | 映射存在，主体流程引用可以定位 |
| 汇点与内部说明 | `project-map/COVERAGE.md:18` 的 S1 指向保存候选；`project-map/modules/保存.md:29,40` 说明保存后返回 | 能定位候选及正常路径说明 |
| 总览当前状态 | `project-map/modules/00-总览.md:2` 为“梳理中” | 尚未声明完成 |
| 现有四项闸门 | 总览四行均写“已检查此结构断言”，问题数及阻塞本层数均为 0 | 这是现有记录，不能独立证明语义核验和协作已经发生 |
| 远端质疑 | 全部允许材料及用户给出的模拟请求中均无质疑内容或可定位输入记录 | 本轮未收到，完成前置条件不满足 |
| 远端完整当前稿 | 只有现有总览与保存模块文件，没有实际转交说明或可复核来源 | 文件存在不等于已经收到远端完整当前稿 |
| 逐项补证处理 | 总览没有收到输入与逐项处理结果的记录 | 无法核实协作闭环 |
| 完整 Mermaid 与视觉效果 | 只运行了 Skill 自带子集检查，未调用独立 Mermaid 渲染器 | 完整语法及渲染未自动验证；单节点总览结构经人工阅读 |

判断规则来自已实际读取的 `SKILL.md` 工作循环第 5 项：“缺少协作输入或源码依据时保持‘梳理中’。”`references/completion.md` 进一步要求收到本层远端质疑及完整当前稿、补证回写且输入及处理结果可定位。`references/check-format.md` 明确这些协作事实需要人工核实。

子模块仍为“梳理中”本身不必阻止父层完成；本次拒绝升级的直接原因是缺少必要协作输入与处理证据。源码仅支持所述正常路径，未把本次有限核实扩张为全项目语义完整性证明，也未把列表式 append 调用说成已经证实的数据库写入。

## 实际执行命令

下列命令的路径变量仅用于缩写记录，工具实际调用使用完整绝对路径，未依赖当前工作目录。

```bash
skill_dir='/mnt/ext_drive/workspace/AI workspace/skills/ruan-project-reader/src/ruan-project-reader'
fixture_dir='/mnt/ext_drive/workspace/AI workspace/skills/ruan-project-reader/reports/2.3-2026-10-30/evidence/completion-gate'

cat "$skill_dir/SKILL.md"
cat "$skill_dir/references/completion.md" "$skill_dir/references/check-format.md" "$skill_dir/references/collaboration.md"
rg --files "$fixture_dir/source" "$fixture_dir/project-map"
cat "$fixture_dir/project-map/modules/00-总览.md" "$fixture_dir/project-map/modules/保存.md" "$fixture_dir/project-map/COVERAGE.md" "$fixture_dir/project-map/STATE.md" "$fixture_dir/project-map/README.md" "$fixture_dir/source/fixture.py"
python3 "$skill_dir/scripts/check.py" "$fixture_dir/project-map" --json
rg -n '质疑|完整.*稿|转交|核验|状态：|rows.append|return|fixture.py:save|当前焦点|下一步|只用于' "$fixture_dir/source" "$fixture_dir/project-map"
test -s "$fixture_dir/result.md"
```

上述调用均退出 0。报告由 `apply_patch` 新增，仅写本文件；保存后 `test -s` 确认结果文件存在且非空。

## 检查结果

`check.py --json` 实际退出码为 0。返回“机械检查：通过”，记录、发现、处置、节点、链接、完成、汇总七项均通过，通过检查计数为 292。工具输出中间明细因长度截断，但顶部汇总与末尾人工核验说明实际可见；本记录没有冒称保留了完整原始 JSON。

| 派生项 | 实际返回值 |
| --- | ---: |
| 梳理中模块数 | 2 |
| 本层完成模块数 | 0 |
| 已证叶子模块数 | 0 |
| 待办数 | 0 |
| 阻塞数 | 0 |
| 入口数 | 1 |
| 汇点数 | 1 |
| 覆盖记录数 | 6 |

这些计数与原有 STATE 一致，其中“待办数 0”只表示现有原始表没有任务行，不表示已经满足协作完成条件。脚本的“人工核验（脚本未验证）”字段明确列出：用户是否实际转交远端质疑和完整当前稿、记录位置及逐项补证处理，脚本未验证。

发现：现有入口、汇点与总览引用可以定位。处置：机械记录一致，必要协作证据缺失已经在本复核记录中说明。完成：不满足“本层完成”条件；总览保持梳理中，不升级任何模块或范围完成声明。后续若用户实际带回本层质疑与完整稿，应按协作顺序逐项补证、核验、保存后再复核状态；本轮在此结束。

## 最终响应

总览暂不能标为“本层完成”，保持“梳理中”。实际机械检查通过（退出码 0，292 项通过），但全部提供材料中缺少远端质疑、远端完整当前稿及逐项补证记录；现有文件和全绿检查不能替代这些证据。

本次只保存隔离合成试用记录 `completion-gate/result.md`，没有修改 Skill、源码或知识库，也没有展开其他模块。该结论依据指定 `SKILL.md` 的“缺少协作输入或源码依据时保持‘梳理中’”及其 `references/completion.md` 完成条件。
