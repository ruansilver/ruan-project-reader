"""Contract regressions: positive records, injected faults, unknown propagation, read-only CLI."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
SCRIPT = BASE.parent / "ruan-project-reader/scripts/check.py"
spec = importlib.util.spec_from_file_location("project_reader_check", SCRIPT)
check = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = check
spec.loader.exec_module(check)
MODULE = "modules/保存.md"
OVERVIEW = "modules/00-总览.md"


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="reader 中文 space ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project-map"
        shutil.copytree(BASE / "fixtures/valid-map", self.root)

    def replace(self, file, old, new):
        path = self.root / file
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def report(self):
        return check.Checker(self.root).run()

    def unfinished(self):
        self.replace("COVERAGE.md", "本轮范围整体完成：是", "本轮范围整体完成：否")
        self.replace(MODULE, "状态：已证叶子", "状态：梳理中")
        self.replace("STATE.md", "梳理中模块数：0", "梳理中模块数：1")
        self.replace("STATE.md", "已证叶子模块数：1", "已证叶子模块数：0")

    def task(self, source="新增调查", kind="待核实", problem="检查调用边界"):
        with (self.root / MODULE).open("a", encoding="utf-8") as f:
            f.write(f"| {source} | {kind} | {problem} | 读取调用体 | 检索实现 | 契约尚缺 | 出口不明 | 获取契约后重试 |\n")

    def test_valid(self):
        r = self.report()
        self.assertEqual(r["机械检查"], "通过", r["明细"])
        self.assertEqual(r["派生计数"]["覆盖记录数"], 6)
        self.assertTrue(r["人工核验（脚本未验证）"])

    def test_fault_injection(self):
        cases = [
            ("count_mismatch", MODULE, "检查对象数：1", "检查对象数：3", "处置"),
            ("zero_row", MODULE, "| 1 | 本文已解释", "| 0 | 本文已解释", "处置"),
            ("merged_trigger", MODULE, "| 1 | 本文已解释", "| 2 | 本文已解释", "处置"),
            ("trigger_trivial", MODULE, "| 本文已解释 |", "| 琐碎 |", "处置"),
            ("category", MODULE, "| 写库缓存状态 |", "| 写库 |", "处置"),
            ("disposition", MODULE, "| 本文已解释 |", "| 随便处理 |", "处置"),
            ("missing_field", MODULE, "扫描方法：逐行读 fixture.py 的 save 和返回", "", "处置"),
            ("duplicate_field", MODULE, "检查对象数：1", "检查对象数：1\n检查对象数：1", "处置"),
            ("negative", MODULE, "检查对象数：1", "检查对象数：-1", "处置"),
            ("missing_note", MODULE, "| B | 返回 | 返回保存结果 | 无 |", "", "节点"),
            ("duplicate_note", MODULE, "| B | 返回 | 返回保存结果 | 无 |", "| A | 保存 | 返回保存结果 | 无 |", "节点"),
            ("label", MODULE, "| B | 返回 |", "| B | 结束 |", "节点"),
            ("broken_link", OVERVIEW, "(保存.md)", "(不存在.md)", "链接"),
            ("bad_anchor", MODULE, "(#规则)", "(#不存在)", "链接"),
            ("bad_state", MODULE, "状态：已证叶子", "状态：完成", "完成"),
            ("bad_limit", MODULE, "限制：无", "限制：也许", "完成"),
            ("leaf_limit", MODULE, "限制：无", "限制：有", "完成"),
            ("gate_missing_row", MODULE, "| 未决 → 处置 | 合成夹具全范围 | 1 | 0 | 0 | 已检查此结构断言 |", "", "完成"),
            ("blocked_gate", MODULE, "| 1 | 0 | 0 | 已检查此结构断言 |", "| 1 | 1 | 1 | 阻塞 |", "完成"),
            ("state_count", "STATE.md", "待办数：0", "待办数：1", "汇总"),
            ("coverage_count", "STATE.md", "覆盖记录数：6", "覆盖记录数：2", "汇总"),
            ("entry_node", "COVERAGE.md", "总览.md#F", "总览.md#X", "发现"),
            ("entry_flow", "COVERAGE.md", "[保存](modules/保存.md)", "[保存](README.md)", "发现"),
            ("sink_mapping", "COVERAGE.md", "| S1 | fixture.py:save |", "| S1 | other.py:write |", "发现"),
            ("same_direction", "COVERAGE.md", "| 正向入口 | 反向汇点 | 全夹具", "| 正向入口 | 正向入口 | 全夹具", "发现"),
            ("new_candidates", "COVERAGE.md", "从写入回查入口 | 1 | 0 |", "从写入回查入口 | 1 | 1 |", "发现"),
            ("missing_direction", "COVERAGE.md", "| 盲区审查 |", "| 另一个方向 |", "发现"),
            ("false_convergence", "COVERAGE.md", "本轮发现暂时收敛：是", "本轮发现暂时收敛：否", "完成"),
            ("node_todo_empty", MODULE, "| A | 保存 | 写入记录后返回结果 | 无 |", "| A | 保存 | 写入记录后返回结果 | 待办：[缺口](#未决) |", "节点"),
        ]
        original = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*.md")}
        for name, path, old, new, group in cases:
            with self.subTest(name=name):
                for rel, data in original.items():
                    (self.root / rel).write_bytes(data)
                self.replace(path, old, new)
                r = self.report()
                self.assertEqual(r["机械检查"], "失败")
                self.assertEqual(r["分项"][group], "失败", r["明细"])

    def test_each_trigger_not_trivial(self):
        original = (self.root / MODULE).read_text(encoding="utf-8")
        for category in check.CATEGORIES[:7]:
            with self.subTest(category=category):
                (self.root / MODULE).write_text(original.replace("写库缓存状态", category).replace("| 本文已解释 |", "| 琐碎 |"), encoding="utf-8")
                self.assertEqual(self.report()["分项"]["处置"], "失败")

    def test_unknown_quantity_never_zero(self):
        self.unfinished()
        self.replace(MODULE, "| 1 | 本文已解释", "| 未知 | 本文已解释")
        r = self.report()
        self.assertEqual(r["机械检查"], "未验证")
        self.assertIsNone(r["派生计数"]["待办数"])

    def test_malformed_table_not_empty(self):
        self.unfinished()
        self.replace(MODULE, "| --- | --- | --- | --- | --- | --- |", "| --- | --- | --- | --- |")
        r = self.report()
        self.assertNotEqual(r["机械检查"], "通过")
        self.assertIsNone(r["派生计数"]["待办数"])

    def test_unknown_mermaid(self):
        self.replace(MODULE, '  A["保存"]', '  subgraph X["分组"]\n  A["保存"]\n  end')
        self.assertEqual(self.report()["机械检查"], "未验证")

    def test_reference_link_unknown(self):
        with (self.root / "README.md").open("a", encoding="utf-8") as f:
            f.write("\n[示例][target]\n[target]: modules/保存.md\n")
        self.assertEqual(self.report()["机械检查"], "未验证")

    def test_outbound_url_not_fetched(self):
        with (self.root / "README.md").open("a", encoding="utf-8") as f:
            f.write("\n[外链](https://example.invalid/test)\n")
        self.assertEqual(self.report()["机械检查"], "未验证")

    def test_multiple_tasks_same_module_count_separately(self):
        self.unfinished()
        self.task("同一来源", problem="调用场景甲")
        self.task("同一来源", problem="调用场景乙")
        self.replace("STATE.md", "待办数：0", "待办数：2")
        self.assertEqual(self.report()["机械检查"], "通过")
        p = self.root / MODULE
        lines = p.read_text(encoding="utf-8").splitlines()
        p.write_text("\n".join(x for x in lines if "调用场景甲" not in x) + "\n", encoding="utf-8")
        self.replace("STATE.md", "待办数：2", "待办数：1")
        self.assertEqual(self.report()["机械检查"], "通过")

    def test_standalone_blocked_task(self):
        self.unfinished()
        self.task(kind="阻塞")
        self.replace("STATE.md", "待办数：0", "待办数：1")
        self.replace("STATE.md", "阻塞数：0", "阻塞数：1")
        self.assertEqual(self.report()["机械检查"], "通过")

    def test_missing_blocked_detail_fails(self):
        self.unfinished()
        self.task(kind="阻塞")
        self.replace(MODULE, "获取契约后重试", "无")
        self.assertEqual(self.report()["分项"]["处置"], "失败")

    def test_pending_candidate_carried_once(self):
        self.unfinished()
        self.replace(MODULE, "| 本文已解释 | [规则](#规则)", "| 待核实 | [未决](#未决)")
        self.task("fixture.py:save / 保存记录")
        self.replace("STATE.md", "待办数：0", "待办数：1")
        self.assertEqual(self.report()["机械检查"], "通过")

    def test_uncarried_candidate_count_unknown(self):
        self.unfinished()
        self.replace(MODULE, "| 本文已解释 | [规则](#规则)", "| 待核实 | [未决](#未决)")
        r = self.report()
        self.assertEqual(r["机械检查"], "未验证")
        self.assertIsNone(r["派生计数"]["待办数"])

    def test_leaf_cannot_hide_tasks(self):
        self.task()
        self.assertEqual(self.report()["分项"]["完成"], "失败")

    def test_independent_limitation_counted(self):
        self.unfinished()
        self.replace(MODULE, "限制：无", "限制：有")
        with (self.root / MODULE).open("a", encoding="utf-8") as f:
            f.write("\n## 限制说明\n问题：契约未知\n已尝试方法：查公开文档\n缺失依据：生产配置\n影响：重试时序未知\n重试条件：获得配置\n")
        self.replace("STATE.md", "待办数：0", "待办数：1")
        self.assertEqual(self.report()["机械检查"], "通过")

    def test_shared_module_multiple_entries(self):
        self.replace(OVERVIEW, "E1 触发", "E1、E2 触发")
        self.replace("COVERAGE.md", "| E1 | fixture.py:save | [保存](modules/保存.md) | [保存流程](modules/00-总览.md#F) | 无 |", "| E1 | fixture.py:save | [保存](modules/保存.md) | [保存流程](modules/00-总览.md#F) | 无 |\n| E2 | fixture.py:other | [保存](modules/保存.md) | [保存流程](modules/00-总览.md#F) | 无 |")
        self.replace("STATE.md", "入口数：1", "入口数：2")
        self.replace("STATE.md", "覆盖记录数：6", "覆盖记录数：7")
        self.assertEqual(self.report()["机械检查"], "通过")

    def test_crlf(self):
        for p in self.root.rglob("*.md"):
            p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(self.report()["机械检查"], "通过")

    def test_cli_read_only_and_exit_codes(self):
        def snapshot():
            return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob("*") if p.is_file()}
        before = snapshot()
        proc = subprocess.run([sys.executable, str(SCRIPT), str(self.root), "--json"], capture_output=True, text=True, cwd=self.tmp.name)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["机械检查"], "通过")
        self.assertEqual(snapshot(), before)
        self.replace(MODULE, '  A["保存"]', '  A@{ shape: rect, label: "保存" }')
        proc = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True)
        self.assertEqual(proc.returncode, 2)
        self.replace("STATE.md", "待办数：0", "待办数：9")
        proc = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True)
        self.assertEqual(proc.returncode, 1)

    def test_missing_root(self):
        self.assertEqual(check.Checker(self.root / "absent").run()["机械检查"], "失败")

    def test_non_utf8_is_unverified(self):
        (self.root / "README.md").write_bytes(b"\xff\xfe\x80")
        self.assertEqual(self.report()["机械检查"], "未验证")

    def test_unreadable_module_counts_not_partial(self):
        (self.root / MODULE).write_bytes(b"\xff\xfe\x80")
        r = self.report()
        self.assertIsNone(r["派生计数"]["已证叶子模块数"])
        self.assertIsNone(r["派生计数"]["待办数"])

    def test_duplicate_candidate_blocks_not_silently_ignored(self):
        self.unfinished()
        p = self.root / MODULE
        body = p.read_text(encoding="utf-8")
        block = body.split("## 候选记录", 1)[1].split("## 闸门记录", 1)[0]
        p.write_text(body + "\n## 候选记录\n" + block, encoding="utf-8")
        r = self.report()
        self.assertNotEqual(r["机械检查"], "通过")
        self.assertIsNone(r["派生计数"]["待办数"])

    def test_search_method_with_pipe_is_not_table(self):
        self.replace(MODULE, "扫描方法：逐行读 fixture.py 的 save 和返回", '扫描方法：rg -n "save|return" fixture.py')
        self.assertEqual(self.report()["机械检查"], "通过")

    def test_pending_candidate_with_detailed_limitation(self):
        self.unfinished()
        self.replace(MODULE, "限制：无", "限制：有")
        self.replace(MODULE, "| 本文已解释 | [规则](#规则)", "| 待核实 | [未决](#未决)")
        self.task("fixture.py:save / 保存记录", kind="限制")
        self.replace("STATE.md", "待办数：0", "待办数：1")
        self.assertEqual(self.report()["机械检查"], "通过")
        self.replace(MODULE, "| 读取调用体 |", "| 无 |")
        self.assertEqual(self.report()["分项"]["处置"], "失败")

    def test_realistic_forward_draft(self):
        fixture = BASE / "fixtures/forward-reviewed"
        r = check.Checker(fixture / "project-map").run()
        self.assertEqual(r["机械检查"], "通过")
        self.assertEqual(r["派生计数"]["待办数"], 9)
        self.assertEqual(r["派生计数"]["阻塞数"], 0)
        self.assertEqual(r["派生计数"]["已证叶子模块数"], 0)
        baseline = json.loads((fixture / "source-baseline.json").read_text(encoding="utf-8"))
        actual = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE / "fixtures/source").iterdir() if p.is_file()}
        self.assertEqual(actual, baseline)


if __name__ == "__main__":
    unittest.main()
