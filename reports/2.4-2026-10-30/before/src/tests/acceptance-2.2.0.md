# ruan-project-reader 2.2.0 验收记录

日期：2026-10-29（Asia/Singapore）。目标：设计 2.2，对应工程三段版本 `2.2.0`。

## 设计来源与初始状态

用户明确要求按当前工程约定生成 2.2，原始设计标题标明“定稿”。据此新增 [2.2.0.md](../../design/versions/2.2.0.md)，仅补 `version/status/previous_version` frontmatter；正文与用户的 [2.2 原稿](../../design/versions/2.2/ruan-project-reader%20Skill%20设计规范（2.2）.md) 字节一致。原稿、两份 Demo、1.6.2 设计均保留。

| 初始核查 | 结论与处理 |
| --- | --- |
| 目标元数据 | 原稿未位于标准 `*.md` 路径且缺 frontmatter；依据本次明确开发指令登记 2.2.0 approved |
| 开发源 | 为空，无有效 SKILL.md；2.2 需求初始均未在开发源满足 |
| 已发布成品 | 1.6.2，原设计哈希和成品哈希均吻合；无手改或哈希冲突 |
| 旧版与新设计 | 固定三层、唯一父树及旧状态体系不能沿用；按新执行网络重建 |
| Demo 可复用部分 | 采用 ChatGPT Demo 的只读 check 基础；从另一 Demo 保留九份玩具源码作为测试输入 |
| Demo 不采用部分 | 厂商路径、present_files、自动写状态命令、测试进入安装包、对未知补零、永远无法通过的覆盖统计 |
| Git | 工程目录无 `.git`，Git 状态不可用；没有初始化、提交、推送或 Tag |

## 设计逐项对应

以下“已验证”区分人工语义审查、机械回归和有限样例行为，不能解释为对所有代码库的效果证明。

| 验收项／设计位置 | 实现位置 | 验证证据与结论 |
| --- | --- | --- |
| A01 当前授权源码、只读业务代码、证据与未知 §1 | SKILL.md；references/modules.md | 人工审查；独立样例明确声明缺失实现与未运行，保留源码基线 |
| A02 执行网络、多入口、无固定树／深度 §2.1、4.2 | SKILL.md；references/modules.md、discovery.md | 人工审查；样例识别请求、消息、定时三个主体，未按目录建树 |
| A03 先内联、独立价值和复用场景差异 §2.2 | references/modules.md；模块与转交模板 | 人工审查；样例未仅为共享接口／Mapper 抽公共流程；多入口共享文档正例回归 |
| A04 触发表、深层工作位置、一跳不是终点 §3.1–3.2 | references/modules.md；check.py | 七触发类别拒绝琐碎子用例；样例追到 afterCommit 内 publish |
| A05 有限候选、九类别、六处置、数量 §3.3、5.1 | check.py；references/check-format.md | 数量、枚举、空集合、合并项、解析异常回归已验证 |
| A06 外部黑盒契约，受限不能伪装已核实 §3.3 | references/modules.md；转交模板 | 样例保留库存、消息、短信和运行装配限制，未擅自宣称外部成功 |
| A07 叶子反证、未处置零、无限制、可重开 §3.3、8 | references/completion.md；check.py | 叶子限制／未决／闸门错误注入；语义反证须人工，不能脚本证明 |
| A08 父子边界契约与本场景出口 §3.4 | references/modules.md、completion.md | 人工审查；不要求后代全部完成，但重要出口缺失阻塞本层 |
| A09 正向入口、反向汇点、隐式装配与盲区 §4.1 | references/discovery.md；COVERAGE 模板 | 样例 3 入口、6 汇点；未把 Feign 出向声明当服务入口；动态装配留限制 |
| A10 汇点须具体候选／正文定位 §4.1、5.2 | check.py coverage | 汇点错位注入失败；不以文件存在或理论可达替代定位 |
| A11 换方向复查、零新增、暂时收敛 §4.2 | discovery.md；check.py coverage | 同方向／非零新增／缺方向回归失败；样例记录汇点反查入口 |
| A12 用户召回探针可选、漏报回查 §4.2 | discovery.md；COVERAGE 模板 | 人工审查；样例如实记未提供，不伪造用户独立探针 |
| A13 原始任务逐条计数，不按模块去重 §5.1、9 | check.py summary；check-format.md | 同来源两个任务依次 2→1、候选引用不重复计数、独立阻塞／限制回归 |
| A14 图节点短注一一对应及有效下钻 §5.2、7.2 | check.py mermaid/node_notes | 缺／重短注、标签不符、空待办锚点失败；不支持图法未验证 |
| A15 链接、入口与总览实际映射 §5.2、7.1 | check.py local_links/coverage | 断链、错锚点、假总览节点、主体指向非模块均失败 |
| A16 状态、限制、闸门合法性 §5.2、8.2 | check.py module/gates | 非法状态、缺闸门项、阻塞非零、受限叶子失败 |
| A17 通过／失败／未验证与退出码 §5.2 | check.py CLI；check-format.md | 0/1/2、失败优先、无法解析不补零、只读快照回归 |
| A18 机械检查不证明业务语义与发现完整 §5.2 | SKILL.md；check.py MANUAL | 输出独立人工核验范围；有限解析未冒称完整 Mermaid 校验 |
| A19 双 AI 角色、完整稿、人工转交 §6 | collaboration.md；remote-relay.md | 独立试用输出可转交代码块；尚无远端回复时保留待审状态，无直接通信 |
| A20 最小知识库、总览普通模块 §7.1 | templates；SKILL.md | 样例有 README、STATE、COVERAGE、总览和三份流程稿；不另画 README 总览 |
| A21 总览节点入口序号、跨流程边与候选 §7.1 | discovery.md；模板 | 样例暴露状态媒介易漏问题后补清说明并复核；不能把非直接调用等同无关系 |
| A22 一图一短注、真实执行／结果、Figma 非门槛 §7.2 | completion.md；模板 | 人工审查；基础节点检查，真实渲染未执行且明确说明 |
| A23 本层／叶子／整体三种完成 §8.1 | completion.md；check.py | 整体完成额外核查收敛、未决、限制、映射和扫描缺口 |
| A24 四项反向闸门、零结果、不适用理由 §8.2 | templates/gates.md；check.py gates | 四项结构、计数、阻塞判定回归；是否支持真实结论仍需源码核验 |
| A25 阻塞本层正面判据与外部边界 §8.2 | completion.md；modules.md | 人工语义审查，未将访问权限当运行契约证据 |
| A26 两轮停滞、受限阶段交付 §8.3 | SKILL.md；completion.md | 指令审查已验证；未伪造真实两轮远端往返，运行行为仍需真实项目观察 |
| A27 串行、逐项复用、当前文件优先 §9 | SKILL.md；collaboration.md | 指令审查；多任务逐条计数及当前记录重派生回归；真实多会话长期恢复未实测 |
| A28 完整未决交接与授权边界 §6、9 | collaboration.md；remote-relay.md | 样例转交包含证据内容和完整未决，不只给路径；源码哈希可复核 |
| A29 跨平台加载和无厂商依赖 | SKILL.md；标准 frontmatter；可选 openai.yaml | Skill Creator 校验通过；Python 3.12.3 标准库运行，中文空格路径和 CRLF 回归；其他 Harness 实机未测试 |
| A30 源构建、发布清单和失败保留 | ../build_release.py；test_release.py | 数字版本比较、draft 排除、冲突拒绝、规范哈希、排除缓存、幂等及失败回滚回归 |

## 自动测试与试用修正

`python3 -m unittest discover -s src/tests -v`：35 个测试方法，包含 29 个契约缺陷注入场景和七类触发项子用例。基础正例、人工待核实正例、共享引用、同模块多任务、限制计数、CLI、发布事务及独立试用真实记录均已覆盖；最终执行结果见下方发布验证。

`skill-creator/scripts/quick_validate.py src/ruan-project-reader`：通过。此工具只检查 Skill 结构，不替代本表语义审查。

已复现并修复的缺陷：

1. Demo 的覆盖记录数永远未知。实现口径定义为入口＋汇点＋发现方法＋交叉复查原始行数，模板与派生一致；不称覆盖率。
2. 整体完成未核查异向零新增、未决和限制。新增机械约束及反例。
3. 重复候选区块被忽略。重复块明确未验证，待办不以局部记录当完整值。
4. 无法读取模块仍给出局部模块计数。模块清点不完整时计数未知。
5. 扫描方法中的正则 `|` 被当表头。仅显式 pipe 表行进入表解析，并保留真实扫描命令。
6. 受限待核实与原始限制记录无法衔接。按同来源承接并要求下一步，保留真实类型；不为过检改成阻塞。
7. 独立试用将没有直接调用误解为没有状态媒介关系。补明确规则：核对写入对象／状态与扫描谓词后标注跨流程交接，不凭表名强连。

独立试用最终结果已固化为 [回归夹具](fixtures/forward-reviewed/README.md)：4 个梳理中模块、3 入口、6 汇点、23 候选、9 条未决、15 条覆盖记录；885 项机械检查通过。九份源码哈希未变，没有外发材料或伪造远端回复。转交稿包含完整当前图文、证据与未决。候选仍有六条待核实，模块均受限，因此脚本通过并未导致提前完成。

## 验证边界

- 独立试用是一个具有限制的玩具项目首轮本地阅读，不是完整双 AI 往返、生产项目验收或全库发现率证明。
- 未执行 Claude Code、DeepSeek Harness 或 Windows 的真实加载及全流程；已完成厂商依赖审查、标准目录校验和可移植运行条件说明。DeepSeek Harness 未指定发行版，不能保证其具体发现目录。
- Python 3.10 为声明的最低语法版本，实际执行环境为 Python 3.12.3；未在每个 Python 小版本测试。
- Mermaid 完整解析／渲染、真实 Figma 效果未验证；这不是设计要求的实施门槛，脚本明确保留人工项。
- 原有 `src/.work/` 含先前工作的唯一材料，未经价值确认不删除；本轮临时输出在提取有价值证据后清理。

实现的跨平台边界参考 [Agent Skills 规范](https://agentskills.io/specification) 与 [Claude Code Skills 官方文档](https://code.claude.com/docs/en/skills)。不会把平台未实测写成已实测，也不会把脚本通过写成语义完整。

## 发布验证

目标版本与当前已发布版本均为 **2.2.0**。执行 `PYTHONDONTWRITEBYTECODE=1 python3 src/build_release.py --build` 时，35 个测试全部通过，然后从开发源生成了 14 个交付文件和独立的 `install/.release.json`。安装目录只包含 SKILL、可选 Codex 界面元数据、五份参考、六份模板和只读检查器，不含测试、缓存、实验记录或 `.gitkeep`。

随后实际执行：

- `python3 src/build_release.py --verify`：目标／已发布版本、设计哈希、成品哈希和源文件一致。
- Skill Creator 对 `install/ruan-project-reader` 的 `quick_validate.py`：通过。
- 安装版 `scripts/check.py` 对基础契约夹具：机械检查及七个分项全部通过，人工核验边界另列。

发布清单派生值：

```text
design_sha256:   107cbdbef401a68cb897e0602dfc3f9f5a357dffd4d906318d5fa3e3a22e36e8
artifact_sha256: babd1396f0c11a9b804a92c7ce29a332121212c65ea929268e7967a3924c2170
```

未完成项仅为上述真实平台加载、完整远端协作与长期项目使用的待验证范围，不冒充已经测试。没有已知尚未落实的 2.2 设计实现项。Git 仍不可用；未初始化、提交、推送或创建 Tag。已保留本轮有价值试用结果为回归夹具，再清理本轮临时目录；原有实验目录未改动。
