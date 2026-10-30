# 回归与验收

当前正式版为 2.3（工程版本 2.3.0）。36 项回归保留既有 35 项，增加未展开入口登记，并把重复待办消解扩展到 2→1→0；行为证据及未验证范围见 [2.3 报告](../../reports/2.3-2026-10-30/report.md)。

在工程根目录运行（Python 3.10+，标准库）：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s src/tests -v
python3 src/ruan-project-reader/scripts/check.py src/tests/fixtures/valid-map
python3 src/build_release.py --verify
```

Windows 可用合适的 `py -3` 并在环境中设置 `PYTHONDONTWRITEBYTECODE=1`；测试会在带中文和空格的临时目录执行。测试不依赖模型接口、网络、Java 编译环境或生产数据。

- `test_check.py`：完备夹具正例、错误注入、未知值传播、共享模块／多任务计数、CLI 退出码及只读性。
- `test_release.py`：数字版本选择、草案排除、冲突、规范哈希、构建过滤、重复构建、失败保留原成品与替换异常回滚。
- `fixtures/valid-map/`：人为构造的记录契约夹具，只验证机械规则，不能作为真实项目已理解的证据。
- `fixtures/source/`：从用户提供的压缩 Demo 选取的九份玩具源码，用于独立行为试用。依赖和构建文件不全，不能编译或声称真实系统运行通过。
- `fixtures/forward-reviewed/`：独立试用后经针对性修订的首轮待审稿，用于真实复杂记录回归；包含可转交提示词、源码基线和最终检查摘要。
- `acceptance-2.2.0.md`：设计逐项对应、行为试用观察和验证边界。

`src/build_release.py --build` 会先重跑回归，再验证现有成品和设计，暂存完整副本后替换 `install/`。语义验收仍须由维护者对照设计与行为结果完成；测试通过不能自动证明全部需求已实现。此开发脚本和测试均不进入安装包。
