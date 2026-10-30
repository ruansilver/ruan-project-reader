# 回归与验收

测试目标为 2.4（工程版本 2.4.0）。保留全部原有36项回归，合法旧库的总结果按只读兼容契约改为未验证，原分项/错误注入/源码哈希断言继续有效；新增验收、规范化、范围清单和隔离流程执行测试。结果及边界见 [2.4报告](../../reports/2.4-2026-10-30/report.md)。

在工程根目录运行（Python 3.10+，标准库）：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s src/tests -v
python3 src/ruan-project-reader/scripts/check.py src/tests/fixtures/valid-map
python3 src/build_release.py --verify
```

Windows 可用合适的 `py -3` 并在环境中设置 `PYTHONDONTWRITEBYTECODE=1`；测试会在带中文和空格的临时目录执行。测试不依赖模型接口、网络、Java 编译环境或生产数据。

- `test_acceptance.py`：单文件/范围指纹、CommonMark围栏、UTF-8/BOM/CRLF、九统计、待验收及个别/整体验收负例、只读CLI、显式整库迁移、重开及哈希恢复后的整体撤销。用户/远端输入均模拟；流程演练不证明自主代理或真实Goal能够暂停。
- `test_check.py`：完备夹具正例、错误注入、未知值传播、共享模块／多任务计数、CLI 退出码及只读性。
- `test_release.py`：数字版本选择、草案排除、冲突、规范哈希、构建过滤、重复构建、失败保留原成品与替换异常回滚。
- `fixtures/valid-map/`：人为构造的记录契约夹具，保留三状态/八统计格式，只验证机械规则，不能作为真实项目已理解的证据；2.4检查器对合法旧库返回退出2。新契约测试仅在隔离副本上补齐结构，不改历史夹具。
- `fixtures/source/`：从用户提供的压缩 Demo 选取的九份玩具源码，用于独立行为试用。依赖和构建文件不全，不能编译或声称真实系统运行通过。
- `fixtures/forward-reviewed/`：独立试用后经针对性修订的首轮待审稿，用于真实复杂记录回归；包含可转交提示词、源码基线和最终检查摘要。
- `acceptance-2.2.0.md`：设计逐项对应、行为试用观察和验证边界。

`src/build_release.py --build` 会先重跑回归，再验证现有成品和设计，暂存完整副本后替换 `install/`。语义验收仍须由维护者对照设计与行为结果完成；测试通过不能自动证明全部需求已实现。此开发脚本和测试均不进入安装包。


如需保留迁移和重开执行快照，可指定知识库外输出目录：

```bash
READER_EVIDENCE_DIR=reports/2.4-2026-10-30/evidence python3 -m unittest discover -s src/tests -p test_acceptance.py -v
```

模拟记录明确标明来源。文件复制、哈希、检查退出码及状态文件写入实际执行；真实用户授权、真实远端、独立代理暂停、真实Goal自动终止/重触发/中断和长期恢复另需平台实测。不能用回归通过替代这些证据。
