# 2.4 验收报告

日期：2026-10-30（Asia/Singapore）。目标正式版本：2.4 / 2.4.0。结论：**2.4.0 已经用户明确接受未验证范围后正式交付；没有剩余已知实现 FAIL，真实暂停与平台恢复仍为 UNVERIFIED，不宣称全部验收通过。** 原有36项和新增23项共59项回归通过；主仓库构建、正式安装成品检查和ZIP校验通过。用户已授权交付后提交并推送，未授权 Tag。

正式 `install/.release.json` 已为 **2.4.0**，由主仓库 `src/build_release.py --build` 生成，运行文件均未直接编辑。正式安装目录与ZIP的14个文件均与开发源逐字节一致；证据见 `release-build.txt`、`release-verify.txt`、`release-validation.json`。隔离构建记录保留为发布前证据。

## 1. 输入、基线与边界

先读取仓库AGENTS、design/README、版本模板及全部2.4原始要求，再通读开发源、引用、模板、检查器、测试/夹具和构建脚本。用户提供的原始要求全部保持原样。新增2.4.0 approved设计，previous_version=2.3.0；登记不是验收通过声明。

基线HEAD为 `f306bf51537d436647ef7b25e0556ff350777708`。`baseline-tests.txt` 记录36项通过；`baseline-release.txt` 记录2.3.0源/成品/设计哈希一致。`before/` 保存修改前源码、测试、构建脚本、README和install；`before-sha256.json` 保存逐文件SHA-256。缓存和既有 `src/.work` 不纳入开发快照，也未清理；后者102个既有文件另见 `preserved-work-inventory.json`，未把可能唯一的旧实验材料当垃圾删除。

进入时已有：标准安装ZIP被用户移走、`install/ruan-project-reader (2).zip` 未跟踪、`design/versions/2.4/` 未跟踪。本轮不把它们冒充AI改动。正式构建前74个受保护输入/成品/夹具/构建文件哈希不变，见 `preserved-files.json`；构建后正式成品按授权更新，原始要求、历史设计/报告、原夹具/构建脚本和既有工作文件保持不变，见 `release-preservation.json`。用户的 `(2).zip` 字节不变且原位保留，不纳入本次提交。没有修改被阅读项目的功能代码；远端操作仅用于本维护仓库的授权同步。

## 2. 实际修改文件

- `README.md`
- `src/ruan-project-reader/SKILL.md`
- `src/ruan-project-reader/references/check-format.md`
- `src/ruan-project-reader/references/collaboration.md`
- `src/ruan-project-reader/references/completion.md`
- `src/ruan-project-reader/references/discovery.md`
- `src/ruan-project-reader/references/modules.md`
- `src/ruan-project-reader/scripts/check.py`
- `src/ruan-project-reader/templates/COVERAGE.md`
- `src/ruan-project-reader/templates/STATE.md`
- `src/ruan-project-reader/templates/module.md`
- `src/ruan-project-reader/templates/remote-relay.md`
- `src/tests/README.md`
- `src/tests/test_check.py`
- `design/versions/2.4.0.md`
- `src/tests/test_acceptance.py`

另由构建器更新 `install/.release.json`、上述11个运行文件在 `install/ruan-project-reader/` 的对应成品，并从正式成品生成 `install/ruan-project-reader.zip`；其余3个运行文件保持原样。原始修复文档仅按原字节登记，不重写。新增本报告目录的基线、独立diff、命令输出、隔离输入/分阶段证据和构建核验副本。完整交付变更清单见 `release-changed-files.txt`。`src/build_release.py`、`test_release.py`、原有fixtures、历史验收文档和历史设计未修改；运行Skill仍14个文件，无新增数据库、通用状态引擎或长期审批副本。

具体改动：完成路径直接替换为核验→待验收→具体版本认可→独立继续；每模块验收记录和排除式指纹；范围清单NFC/UTF-8排序和单独整体验收；四状态九统计；旧库只读兼容与显式整库迁移。发现/颗粒度规则仅各改一处关口衔接，取证、候选、四闸门和停滞规则保留。差异见 `changes.diff`；实施前映射见 `mapping-before.md`。

## 3. 验收结果（原稿第五节同序）

命令A：`python3 -m unittest discover -s src/tests -v`，59项通过，含原有错误注入子用例，证据 `after-tests.txt` / 最终源码对应的 `staged-build.txt` / 主仓库正式构建 `release-build.txt`。

命令B：`READER_EVIDENCE_DIR=reports/2.4-2026-10-30/evidence python3 -m unittest discover -s src/tests -p test_acceptance.py -v`。迁移/重开证据保存实际文件与check明细。命令C：`python3 reports/2.4-2026-10-30/evidence/roundtrip/exercise.py`，8阶段手工流程重放；源码许可/拒绝两个分支实际执行，源码前后哈希不变。

**证据分级**：标“隔离模拟”的PASS只指对应构造输入、文件动作和断言实际执行成功；测试脚本不是自主代理，也不证明真实用户授权、真实远端往返或代理在真实会话中停止。不存在通过关键词搜索就宣称行为正确的项目。

| # | 结果 | 输入/执行结果与证据 |
| --- | --- | --- |
| 1 | PASS（隔离模拟） | 命令C；remote-initial.md故意漏allowed=false的PermissionError。实际读/执行source/fixture.py后保留梳理中、具体转交反馈；完整修订文件复制后复核待验收。`roundtrip/01-local-rejected`、`02-pending`、`local-feedback.md`、`source-check.json`。真实双AI往返未验证。 |
| 2 | UNVERIFIED | `roundtrip/02-pending`、`03-no-new-input`证明已保存待验收、两次只读重查字节不变；没有独立自主代理的真实停止/重触发试验，不能把脚本不写文件当成真实暂停证据。 |
| 3 | PASS（机械＋隔离模拟） | A的`test_pending_and_missing_approval`：其余条件满足，强改叶子而回答未取得，验收分项FAIL；roundtrip等待现场保留。实际代理持续停留由第2项限制覆盖。 |
| 4 | PASS（隔离模拟） | C的“可以，但请把图改为从左到右”按意见退梳理中，保留回答，再新稿复核。`04-conditional-response`、`05-layout-pending`。未用字符串含“可以”推定认可。 |
| 5 | PASS（隔离模拟） | C的`07-accepted-waiting-continue`只认可当前稿；`08-explicit-next`分别记录一次继续指令，无后续长期授权，未实际启动下一协作单位。 |
| 6 | PASS | A的`test_each_file_approval_and_partial_batch`；A/B各自保存哈希，认可A时B待验收，无集中子文件指纹。迁移分批快照另证。 |
| 7 | PASS | A的`test_reader_changes_invalidate_and_operational_changes_do_not`：六个排除节/状态变化不改哈希；规则事实、限制、图、短注与前置文字改变哈希。待办位于未决。 |
| 8 | PASS | A的规范化、围栏、缺结构、Unicode/空格、CLI测试；独立指定规范字节串核SHA-256。BOM/CRLF/片段末LF等价，反引号/波浪线长度和缩进正确，未闭合/重复关键标题无哈希，新增补充默认纳入。`module-fingerprint.json`、`cli-results.json`。 |
| 9 | PASS（隔离缺工具） | 空PATH执行python3确实FileNotFound，`no-python.txt`；A的未知指纹负例在待验收报UNVERIFIED，有模拟认可仍禁止转正。宿主机实际有Python，没有声称真实宿主缺Python。 |
| 10 | PASS（隔离传递） | A的文件复制/原始文本粘贴字节相同、截断可检测；C完整文件先diff再字节复制。任意真实聊天传递保真未验证时仍须人工核对，不靠正文指纹掩盖传递风险。 |
| 11 | PASS（隔离模拟） | C的布局稿仅TD→LR，`local-layout.diff`由文件工具比较；节点/边/条件/出口/短注/依据/引用复核，哈希改变并重新待验收，未全仓重查。 |
| 12 | PASS（隔离模拟） | C遗漏拒绝出口回源码；B的`migration-4-known-change`在明确相关配置变化输入后从待验收回梳理中，不把用户猜测写成已证事实。 |
| 13 | PASS（隔离模拟） | C的`06-discovery-while-waiting`登记新入口线索、未映射和原始未决；当前读者哈希不变、保持待验收，不启动下一单位。若影响当前事实按第12项回退。 |
| 14 | PASS（文件动作） | B的`scope-2-reopened`只重开保存模块，总览保持个别验收；复核再认可。动作由显式测试步骤执行，不证明任意AI会自动遵守。 |
| 15 | PASS（机械＋文件动作） | A检查未个别验收（含总览）、失配、遗漏/重复/越界/NFC冲突、UTF-8排序、改名及独立重算。B的`scope-1`至`scope-7`实际执行模块重开/覆盖变化→即时整体否→旧哈希恢复仍否→个别认可仍不自动整体认可，含已整体是到覆盖变化后的撤销。 |
| 16 | PASS | 原夹具合法三状态/八统计CLI退出2，全部原7分项仍通过，字节快照不变；原故障注入仍退出1。`legacy.json`、`cli-results.json`及原回归。 |
| 17 | PASS（隔离模拟） | B的`migration-1-read-only`无指令不改；明确模拟备份/整库指令后全量改2.4、保持候选/拟完成类型、整体否；基准未知明示且未伪造新核验，分批仅认可总览，已知变化回梳理中。迁移用文件操作，不新增运行时迁移引擎。 |
| 18 | PASS | A的九统计、父层问题非零/阻塞为零、待验收拟叶子闸门、原叶子/整体负例；旧八项兼容。规范版本不计统计。 |
| 19 | UNVERIFIED | 普通文件重查与状态恢复模拟通过；真实Goal自动终止、自动重新触发、意外中断恢复、独立新会话及长期恢复均未实测。未启动真实Goal，也未冒充平台试验。 |
| 20 | PASS（开发源与正式成品） | 原36+新增23回归；Skill Creator源/正式成品校验；14文件全文审查、逐字节比对、无痕grep和ZIP核对。主仓库正式构建/核验退出0，证据 `release-build.txt`、`release-verify.txt`、`release-validation.json`、`release-no-trace-grep.txt`。 |

汇总：18项在明确限定的机械/隔离范围PASS，2项UNVERIFIED（2、19），0项剩余FAIL。真实双AI往返为跨用例未验证范围。不能声称20项全部通过。

## 4. 排错与歧义处置

1. 原文交叉引用按第四节项目号核对，指纹相关均指向第5项；九项统计=原八项+待验收，规范版本不是第十项。第五节20项序号齐全。未发现需要改动原文的计数/指向错误。
2. 模板九个节名逐字核对。原合成旧夹具简写“规则”且省略部分节，不当作2.4模板；隔离转换保留原“规则”锚点，候选行逐字保留。正式历史夹具不改。
3. 旧库合法总结果从0变2是已批准兼容要求。原36测试没有删除；旧合法正例现在额外断言原7分项仍全通过，避免用UNVERIFIED遮盖回归。
4. 按排除清单纳入所有其余正文，包括一级标题上方和前置文字；正文不NFC，范围路径才NFC并按UTF-8排序。范围自然语言难以机器判断，保守清点所有modules/**/*.md，禁止靠删清单绕过未验收文件。
5. 边界负例复现：活动整体清单清空被错误重建、无法解码模块被误报不存在。定位后分别约束“只有未发起空清单可自动清点”并把无法读取引用传播为未验证；保留 `edge-failing-tests.txt`、`edge-fixed-tests.txt` 和回归。
6. 核验基准未知不推定源码/生效配置未变；仅沿用已有记录并明确未知。用户接受历史成果的不确定性不构成当前源码一致证明；相关已知变化须补证。
7. `src/build_release.py` 实际不生成ZIP，且会整目录替换install。本轮不修改其既有发布事务；主仓库通过原构建/核验后，使用标准库zipfile从正式构建目录生成ZIP，逐成员比对。构建前保存原用户ZIP字节，构建完成后原位恢复并核对哈希；before快照也保留。
8. 用户要求“全部通过后”正式构建；原文第五节明确关键未验证不能当全通过、带限制发布须另行决定。保守解释为不能用模拟替代真实暂停/Goal证据，也不能把最初按条件授权发布当成无条件豁免。先完成可审阅实现、报告和隔离构建，再请用户决定。用户随后明确答复“允许，交付后推送到远端”，据此保留UNVERIFIED并正式构建交付、提交和推送；不把发布许可改写成未测行为的PASS。设计文档中“本次未授权commit、push或Tag”保留登记当时的事实；随后明确授权按用户指令优先生效，记录在本报告及发布记录，不改写已构建的设计哈希。

9. 交付检查中，用户旧ZIP含14文件、5目录且顶层目录名带`(2)`；一次性检查把ZIP总条目数当文件数的断言不适用，核对全部成员后确认与原成品一致，未修改用户ZIP。全量`git diff --check`的空白提示全部位于快照、diff原文和grep证据；这些内容须保持原样，现行源/设计/成品的独立检查通过。详见 `release-user-archive-check.json`、`release-diff-check-summary.json`。

## 5. 全文与无痕审查

`full-review-inventory.json` 记录完整读取的14个运行文件、行数、SHA-256与隔离安装目录字节一致性。逐节核对SKILL、5份引用、6份模板、检查器和agents：入口与细则只有一条核验/验收/继续路径；无额外审批系统；先下研、首轮总览、即时登记、候选逐条、以阻塞本层为准的闸门、停滞/串行/Goal限制保持。新增测试及分阶段知识库以当前核验基准表达，修改背景仅在转交说明/本报告。

`no-trace-grep.txt` 对开发源和隔离安装成品的禁用叙事模式无命中；正式成品又经 `release-no-trace-grep.txt` 检查无命中。`release-validation.json` 记录正式14文件与已全文审查的源/隔离成品一致，沿用该逐节审查结论。正常“结束本次执行”是当前约束，保留；检查器的“2.3”是只读数据契约选择，非旧产品版本标识。历史forward-reviewed测试证据含当时纠错叙事，保持不变且不进入安装包。完整Mermaid渲染、各Harness实际加载与非Linux平台未验证，未删除这些限制以凑无痕结果。

发布后的全仓旧版本逐处分类见 `release-version-residuals.json` 和 `release-version-residuals-raw.txt`，汇总见 `release-version-audit.json`；不带release前缀的同类文件为发布前快照。现行开发入口/检查器文档字符串/help/README/测试目标、正式清单与安装包统一2.4或2.4.0；历史设计/报告、版本排序测试、旧契约识别保留。用户已有旧ZIP原位保留且未纳入本次提交，不代表当前正式安装包。

## 6. 发布状态与剩余限制

主仓库实际执行 `python3 src/build_release.py --build`、`--verify`，均退出0；构建重跑59项回归全通过，安装版check对已验收隔离库退出0，Skill Creator校验通过。正式ZIP可解压，14个成员与开发源、正式成品逐字节相同，不含tests/.work/缓存/.gitkeep。哈希见 `release-validation.json` 与发布记录。

`production-preserved.json`、`production-verify.txt` 保存用户决定前2.3.0成品未变、目标与成品尚不一致的历史现场，不表示当前版本；当前事实以 `release-verify.txt` 和 `install/.release.json` 为准。

真实自主代理暂停/重触发、真实Goal及长期恢复、真实双AI往返、其他平台与完整Mermaid渲染仍未验证。用户允许在明确保留这些限制的前提下正式交付2.4，未要求将其标成PASS。提交和推送已获授权，不创建Tag或GitHub Release；同步结果见发布记录及最终交付回复。

构建事务结束后无残留新src/.work产物；102个既有文件字节不变。用户原有未跟踪ZIP保留。发布前后Git清单及远端同步证据保存在本报告目录；历史报告、原始要求和已发布设计内容不改写。
