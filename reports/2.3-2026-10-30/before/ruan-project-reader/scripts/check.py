#!/usr/bin/env python3
"""ruan-project-reader 2.2.0: 只读、有限的 Markdown 记录契约检查。

机器可读排版约定见 references/check-format.md；它们不是新增设计规则。
退出码：0=机械范围通过；1=存在确定失败；2=存在未验证且无确定失败。
不会读取源码来证明语义，不会修改文档、切换状态或保存 JSON 状态库。
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

CATEGORIES = ("事务锁并发", "写库缓存状态", "MQ异步后台", "异常重试补偿", "权限判断算法", "配置分派", "外部调用副作用", "出向调用", "其他")
DISPOSITIONS = ("本文已解释", "模块引用", "外部边界", "琐碎", "待核实", "阻塞")
STATES = ("梳理中", "本层完成", "已证叶子")
GATES = ("入口 → 结果", "源码 → 流程", "封装 → 隐藏环节", "未决 → 处置")
CANDIDATE_HEADER = ("来源位置", "候选", "类别", "数量", "处置", "证据或去向")
NOTE_HEADER = ("节点 ID", "原标签", "简短说明", "去向")
UNRESOLVED_HEADER = ("来源", "类型", "问题", "下一步", "已尝试方法", "缺失依据", "影响", "重试条件")
GATE_HEADER = ("检查项", "检查范围", "对象数", "问题数", "其中阻塞本层", "说明")
ENTRY_HEADER = ("序号", "来源位置", "主体流程", "总览节点", "下一步")
SINK_HEADER = ("序号", "来源位置", "定位或孤立候选", "下一步")
METHOD_HEADER = ("方法或方向", "适用性", "扫描范围", "扫描方法", "检查对象数", "未检查区域", "新增候选数", "说明")
CROSS_HEADER = ("产生候选的方法或方向", "交叉复查方法或方向", "检查范围", "方法", "检查对象数", "新增候选数", "未检查区域", "未决去向")
SUMMARY_KEYS = ("梳理中模块数", "本层完成模块数", "已证叶子模块数", "待办数", "阻塞数", "入口数", "汇点数", "覆盖记录数")
MANUAL = [
    "隐藏调用、发现漏报、业务语义、源码真实性、证据是否支持分类和处置理由：脚本未验证，须本地核源码并由远端独立质疑。",
    "闸门断言、边界契约、外部黑盒契约、交叉复查的实质差异与真实无新增：脚本未验证。",
    "是否值得独立成模块、叶子反证、总览边的真实执行语义、引用场景可达性：脚本未验证。",
    "执行前复核已有成果是否满足当前任务、是否可消费原始记录：脚本不执行，须本地据实际文件与源码核验。",
    "完整 Mermaid 语法、图形渲染与视觉效果：本脚本只解析文档所述子集，不调用渲染器。",
]
PLACEHOLDER = re.compile(r"待填写|待填|〈|〉|<待|\bTODO\b|^\.{3}$|^…+$|^\?$", re.I)
LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^\n]*?)\)")


def clean(value: str) -> str:
    value = value.strip()
    if value.startswith("**") and value.endswith("**"):
        value = value[2:-2]
    return value.strip().strip("`")


def plain(value: str) -> str:
    return clean(LINK.sub(lambda m: m.group(1), value))


def without_fences(text: str) -> str:
    return re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", text)


def cells(line: str) -> list[str]:
    """支持普通 pipe 表和转义竖线；未转义竖线始终是分列符。"""
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|") and not value.endswith("\\|"):
        value = value[:-1]
    return [clean(re.sub(r"\\\|", "|", x)) for x in re.split(r"(?<!\\)\|", value)]


def links(value: str) -> list[tuple[str, str]]:
    """解析行内链接，保留目标中的成对括号；外链不抓取。"""
    out = []
    for match in re.finditer(r"(?<!!)\[([^\]\n]+)\]\(", value):
        index, start, depth = match.end(), match.end(), 1
        escaped = False
        while index < len(value) and depth:
            char = value[index]
            if char == "\n":
                break
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            index += 1
        if depth:
            continue
        target = value[start:index-1].strip()
        if target.startswith("<") and ">" in target:
            target = target[1:target.index(">")]
        else:
            target = re.sub(r"\s+[\"'].*[\"']$", "", target)
        out.append((match.group(1), re.sub(r"\\([()])", r"\1", target)))
    return out


@dataclass
class Document:
    path: Path
    text: str

    def section(self, name: str) -> str | None:
        lines = without_fences(self.text).splitlines()
        for index, line in enumerate(lines):
            match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
            if match and clean(match.group(2)) == name:
                level = len(match.group(1))
                end = len(lines)
                for i in range(index + 1, len(lines)):
                    following = re.match(r"^(#{1,6})\s+", lines[i])
                    if following and len(following.group(1)) <= level:
                        end = i
                        break
                return "\n".join(lines[index + 1:end])
        return None

    def record_section(self, name: str, header: tuple[str, ...]) -> str | None:
        body = self.section(name)
        if body is not None:
            return body
        # 规范固定的是内容/表头，并未固定章节标题。对唯一匹配表头回溯所在节。
        lines = without_fences(self.text).splitlines()
        matches = [i for i, line in enumerate(lines) if "|" in line and tuple(cells(line)) == header]
        if len(matches) != 1:
            return None
        at = matches[0]
        start, end = 0, len(lines)
        level = 6
        for i in range(at - 1, -1, -1):
            heading = re.match(r"^(#{1,6})\s+", lines[i])
            if heading:
                start, level = i + 1, len(heading.group(1))
                break
        for i in range(at + 1, len(lines)):
            heading = re.match(r"^(#{1,6})\s+", lines[i])
            if heading and len(heading.group(1)) <= level:
                end = i
                break
        return "\n".join(lines[start:end])

    def fields(self, text: str | None = None) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for line in without_fences(self.text if text is None else text).splitlines():
            match = re.match(r"^\s*([^#|：:]+)[：:]\s*(.*?)\s*$", line)
            if match:
                result.setdefault(clean(match.group(1)), []).append(clean(match.group(2)))
        return result


class Checker:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.results: list[dict[str, str]] = []
        self.docs: dict[Path, Document] = {}
        self.modules: dict[Path, dict] = {}
        self.counts: dict[str, int | None] = {}
        self.unresolved_complete = True
        self.raw_counts: dict[str, int | None] = {}
        self.extra_tasks = 0
        self.module_inventory_complete = True

    def record(self, status: str, group: str, path: Path, message: str):
        try:
            where = str(path.relative_to(self.root)) or "."
        except ValueError:
            where = str(path)
        self.results.append({"结果": status, "范围": group, "文件": where, "说明": message})

    def require(self, condition: bool, group: str, path: Path, message: str):
        self.record("通过" if condition else "失败", group, path, message)
        return condition

    def unknown(self, group: str, path: Path, message: str):
        self.record("未验证", group, path, message)

    def read(self, path: Path) -> Document | None:
        path = path.resolve()
        if path in self.docs:
            return self.docs[path]
        if not self.require(path.is_file(), "记录", path, "文件存在"):
            return None
        try:
            doc = Document(path, path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError) as exc:
            self.unknown("记录", path, f"无法读取 UTF-8 文档：{exc}")
            return None
        self.docs[path] = doc
        return doc

    def field(self, doc: Document, name: str, text: str | None = None, group="记录") -> str | None:
        values = doc.fields(text).get(name, [])
        if not self.require(len(values) == 1, group, doc.path, f"字段 {name} 必须恰好出现一次；实际 {len(values)} 次"):
            return None
        value = values[0]
        if not self.require(bool(value), group, doc.path, f"字段 {name} 非空"):
            return None
        if PLACEHOLDER.search(value):
            self.unknown(group, doc.path, f"字段 {name} 仍是占位内容：{value}")
            return None
        return value

    def number(self, value: str | None, doc: Document, context: str, group="记录") -> int | None:
        if value is None:
            return None
        if re.fullmatch(r"-\d+", value):
            self.record("失败", group, doc.path, f"{context} 不得为负数：{value}")
            return None
        if not re.fullmatch(r"\d+", value):
            self.unknown(group, doc.path, f"{context} 无法解析为非负整数：{value!r}，不按零处理")
            return None
        return int(value)

    def table(self, doc: Document, section: str, expected: tuple[str, ...], required=True, group="记录") -> list[dict[str, str]] | None:
        occurrences = sum(tuple(cells(line)) == expected for line in without_fences(doc.text).splitlines() if "|" in line)
        if occurrences > 1:
            self.unknown(group, doc.path, f"{section} 有 {occurrences} 个同类表，不能确认唯一有效记录；请合并当前稿")
            return None
        body = doc.record_section(section, expected)
        if body is None:
            if required:
                self.unknown(group, doc.path, f"未识别 ## {section}；未执行该块检查（排版契约见 check-format.md）")
            return None
        if section == "未决" and body.strip() in ("无", "无。"):
            return []
        lines = without_fences(body).splitlines()
        # A search command may contain regex alternation or a shell pipe. Only
        # explicit pipe-table rows belong to this serialization contract.
        table_lines = [(i, x) for i, x in enumerate(lines) if x.lstrip().startswith("|")]
        if not table_lines:
            if required:
                self.unknown(group, doc.path, f"{section} 无可解析的 pipe 表；不把缺失项当零")
            return None
        start, first = table_lines[0]
        headers = tuple(cells(first))
        if headers != expected:
            status = "失败" if expected in (CANDIDATE_HEADER, GATE_HEADER) else "未验证"
            self.record(status, group, doc.path, f"{section} 表头/列顺序无法匹配：预期 {' / '.join(expected)}；实际 {' / '.join(headers)}")
            return None
        self.record("通过", group, doc.path, f"{section} 表头可解析")
        if start + 1 >= len(lines) or not all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells(lines[start + 1])) or len(cells(lines[start + 1])) != len(expected):
            self.unknown(group, doc.path, f"{section} 表分隔行异常，整块未验证，不按空表处理")
            return None
        rows = []
        ended = False
        for line in lines[start + 2:]:
            if not line.strip():
                ended = True
                continue
            if "|" not in line:
                ended = True
                continue
            if ended:
                self.unknown(group, doc.path, f"{section} 表内中断或包含第二张表，不能确认记录完整性")
                return None
            row = cells(line)
            if len(row) != len(expected):
                self.unknown(group, doc.path, f"{section} 行列数异常：应 {len(expected)} 列，实际 {len(row)} 列；{line.strip()}")
                return None
            if any(PLACEHOLDER.search(value) for value in row):
                self.unknown(group, doc.path, f"{section} 仍有占位行：{line.strip()}")
                return None
            if tuple(row) == expected:
                self.unknown(group, doc.path, f"{section} 出现重复表头，不按有效记录处理")
                return None
            for key, value in zip(expected, row):
                self.require(bool(value), group, doc.path, f"{section} 第 {len(rows)+1} 行 {key} 非空（不适用填“无”并说明必要原因）")
            rows.append(dict(zip(expected, row)))
        self.record("通过", group, doc.path, f"{section} 可解析：{len(rows)} 行")
        return rows

    def unresolved(self, doc: Document) -> list[dict[str, str]] | None:
        rows = self.table(doc, "未决", UNRESOLVED_HEADER, group="处置")
        if rows is None:
            self.unresolved_complete = False
            return None
        # 用户补充：分别登记的原始任务逐条计数；相同来源不自动合并。
        for row in rows:
            source, kind = plain(row["来源"]), row["类型"]
            self.require(kind in ("待核实", "阻塞", "限制"), "处置", doc.path, f"未决 {source} 类型合法：{kind}")
            self.require(row["问题"] not in ("", "无", "无。"), "处置", doc.path, f"未决 {source} 有问题说明")
            fields = ("下一步",) if kind == "待核实" else ("已尝试方法", "缺失依据", "影响", "重试条件")
            for field in fields:
                self.require(row[field] not in ("", "无", "无。"), "处置", doc.path, f"{kind} {source} 具备 {field}")
        return rows

    def carried(self, doc: Document, rows: list[dict[str, str]] | None, source: str, kind: str | None = None, alternative: str | None = None) -> bool:
        if rows is None:
            self.unresolved_complete = False
            return False
        matches = [r for r in rows if plain(r["来源"]) in (source, alternative)
                   and (kind is None or r["类型"] == kind or (kind == "待核实" and r["类型"] == "限制"))]
        if not matches:
            self.unknown("处置", doc.path, f"{source} 未能定位对应未决记录；必需信息是否在其他写法中齐备未验证")
            self.unresolved_complete = False
            return False
        # 多条原始任务可同指一模块；unresolved() 已逐行核对必需字段。
        # 受限的待核实项仍是一个原始任务，不必为检查器把事实改成“阻塞”。
        if kind == "待核实":
            for row in matches:
                self.require(row["下一步"] not in ("", "无", "无。"), "处置", doc.path, f"待核实 {source} 的承接记录具备下一步")
        return True

    def target(self, doc: Document, raw: str) -> tuple[Path | None, str]:
        try:
            parts = urlsplit(raw)
        except ValueError:
            return None, ""
        if parts.scheme or parts.netloc or raw.startswith("//"):
            return None, unquote(parts.fragment)
        return (doc.path.parent / unquote(parts.path)).resolve() if parts.path else doc.path, unquote(parts.fragment)

    def local_links(self, doc: Document):
        body = without_fences(doc.text)
        if re.search(r"\[[^\]\n]+\]\[[^\]\n]*\]", body) or re.search(r"(?m)^\s*\[[^\]]+\]:", body):
            self.unknown("链接", doc.path, "存在引用式 Markdown 链接；该子集未解析，不能声称所有链接已验证")
        for label, raw in links(body):
            path, fragment = self.target(doc, raw)
            if path is None:
                self.unknown("链接", doc.path, f"外部 URL 目标存在性未执行联网验证：{raw}")
                continue
            if not self.require(path.is_file(), "链接", doc.path, f"本地 Markdown 链接目标存在：{raw}"):
                continue
            if fragment and path.suffix.lower() == ".md" and path.is_relative_to(self.root):
                target_doc = self.read(path)
                if target_doc and fragment not in self.anchors(target_doc):
                    info = self.modules.get(path)
                    if info and info.get("nodes") is None:
                        self.unknown("链接", doc.path, f"该锚点可能是未解析图节点，目标定位未验证：{raw}")
                    else:
                        self.record("失败", "链接", doc.path, f"本地 Markdown 锚点不存在：{raw}")
        # 图片不是候选去向；这里只验证普通 Markdown 链接。

    def anchors(self, doc: Document) -> set[str]:
        anchors = set(re.findall(r'<a\s+(?:id|name)=[\"\']([^\"\']+)[\"\']', doc.text, re.I))
        used = Counter()
        for title in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", without_fences(doc.text)):
            title = re.sub(r"[^\w\-\s\u4e00-\u9fff]", "", plain(title).lower())
            slug = re.sub(r"\s+", "-", title.strip())
            suffix = "" if used[slug] == 0 else f"-{used[slug]}"
            anchors.add(slug + suffix)
            used[slug] += 1
        info = self.modules.get(doc.path)
        if info:
            anchors.update(info.get("nodes") or {})  # 节点定位符，必须在实图存在。
        return anchors

    def mermaid(self, doc: Document) -> dict[str, str] | None:
        blocks = re.findall(r"(?ms)^\s*(`{3,}|~{3,})mermaid\s*\n(.*?)^\s*\1\s*$", doc.text)
        graphs = [body for _, body in blocks]
        if not graphs and "mermaid" in doc.text.lower():
            self.unknown("节点", doc.path, "Mermaid 围栏写法无法解析，未验证节点对应")
            return None
        if not self.require(len(graphs) == 1, "节点", doc.path, f"主体恰好一张 Mermaid 图；实际 {len(graphs)} 张"):
            return None
        lines = [x.strip() for x in graphs[0].splitlines() if x.strip() and not x.strip().startswith("%%")]
        if not lines or not re.fullmatch(r"(?:flowchart|graph)\s+(?:TD|TB|BT|LR|RL)\s*;?", lines[0]):
            self.unknown("节点", doc.path, "不支持该 Mermaid 图类型/声明；仅解析 flowchart/graph 子集")
            return None
        nodes: dict[str, str] = {}
        referenced = set()
        unsupported = []
        # 单行节点声明与引用边；不会猜测其他合法 Mermaid 语法。
        node_pattern = re.compile(r'^([A-Za-z_][\w-]*)\s*(\[\[.*\]\]|\(\(.*\)\)|\(\[.*\]\)|\[\(.*\)\]|\{\{.*\}\}|\[.*\]|\(.*\)|\{.*\})\s*;?$')
        edge_pattern = re.compile(r'^([A-Za-z_][\w-]*)\s*(?:-->|---|==>|-\.->)(?:\|[^|]*\|)?\s*([A-Za-z_][\w-]*)\s*;?$')
        shapes = (("[[", "]]"), ("((", "))"), ("([", "])"), ("[(", ")]"), ("{{", "}}"), ("[", "]"), ("(", ")"), ("{", "}"))
        for line in lines[1:]:
            found = node_pattern.fullmatch(line)
            if found:
                ident, shape = found.groups()
                label = None
                for left, right in shapes:
                    if shape.startswith(left) and shape.endswith(right):
                        label = shape[len(left):-len(right)].strip()
                        break
                if label is None or re.search(r"(?:-->|==>|-\.->)", shape):
                    unsupported.append(line)
                    continue
                if label.startswith('"') and label.endswith('"'):
                    label = label[1:-1]
                elif '"' in label or any(x in label for x in ("[", "]", "{", "}")):
                    unsupported.append(line)
                    continue
                label = html.unescape(label)
                if ident in nodes and nodes[ident] != label:
                    self.require(False, "节点", doc.path, f"同一 Mermaid 节点 {ident} 有不一致标签")
                nodes[ident] = label
                continue
            found = edge_pattern.fullmatch(line)
            if found:
                referenced.update(found.groups())
                continue
            if re.fullmatch(r"[A-Za-z_][\w-]*\s*;?", line) and line != "end":
                referenced.add(line.rstrip(";").strip())
                continue
            unsupported.append(line)
        if unsupported:
            self.unknown("节点", doc.path, "Mermaid 存在不支持的输入，节点完整对应未验证：" + " / ".join(unsupported[:3]))
            return None
        for ident in referenced:
            nodes.setdefault(ident, ident)  # Mermaid 未显式声明标签时，ID 即可见标签。
        self.require(bool(nodes), "节点", doc.path, "Mermaid 有可见执行节点")
        return nodes

    def node_notes(self, doc: Document, nodes: dict[str, str] | None):
        notes = self.table(doc, "逐节点短注", NOTE_HEADER, group="节点")
        if notes is None or nodes is None:
            return notes
        ids = [r["节点 ID"] for r in notes]
        self.require(len(set(ids)) == len(ids), "节点", doc.path, "每个节点 ID 恰好一条短注")
        self.require(set(ids) == set(nodes), "节点", doc.path, f"可见节点与短注一一对应；缺短注 {sorted(set(nodes)-set(ids))}；多余短注 {sorted(set(ids)-set(nodes))}")
        for note in notes:
            ident = note["节点 ID"]
            if ident in nodes:
                self.require(html.unescape(note["原标签"]) == nodes[ident], "节点", doc.path, f"{ident} 短注原标签与可见标签一致")
            route = note["去向"]
            marked = any(re.search(r"^(?:下钻|引用)[：:]|[【\[](?:下钻|引用)[】\]]", text) for text in (note["原标签"], note["简短说明"]))
            if route != "无" or marked:
                if route.startswith("待办"):
                    pending_rows = self.modules.get(doc.path, {}).get("unresolved")
                    if pending_rows is None:
                        self.unknown("节点", doc.path, f"{ident} 的待办承接未能解析")
                    else:
                        self.require(any(plain(r["来源"]) == ident for r in pending_rows), "节点", doc.path, f"{ident} 的待办链接有以节点 ID 为来源的实际未决")
                refs = links(route)
                if not self.require(bool(refs), "节点", doc.path, f"{ident} 标识下钻/引用或待办时有实际链接"):
                    continue
                valid = False
                external = False
                for _, target in refs:
                    path, frag = self.target(doc, target)
                    if path is None:
                        external = True
                    elif path.is_file():
                        if path.suffix.lower() == ".md" and (path in self.modules or frag):
                            valid = True
                if not valid and external:
                    self.unknown("节点", doc.path, f"{ident} 外部引用去向未联网验证")
                else:
                    self.require(valid, "节点", doc.path, f"{ident} 去向是有效模块/正文或未决定位")
        return notes

    def gates(self, doc: Document, required: bool, complete: bool):
        if doc.record_section("闸门记录", GATE_HEADER) is None:
            if required:
                self.record("失败", "完成", doc.path, "完成状态缺少闸门记录；四项缺一不可")
            return
        rows = self.table(doc, "闸门记录", GATE_HEADER, required=True, group="完成")
        if rows is None:
            return
        names = [r["检查项"] for r in rows]
        self.require(len(names) == 4 and set(names) == set(GATES), "完成", doc.path, f"闸门四项恰好各一行；实际 {names}")
        for row in rows:
            nums = [self.number(row[x], doc, f"闸门 {row['检查项']} / {x}", "完成") for x in ("对象数", "问题数", "其中阻塞本层")]
            if all(n is not None for n in nums):
                objects, problems, blocked = nums
                self.require(blocked <= problems, "完成", doc.path, f"闸门 {row['检查项']} 其中阻塞本层不超过问题数")
                if complete:
                    self.require(blocked == 0, "完成", doc.path, f"完成状态闸门 {row['检查项']} 其中阻塞本层为 0；实际 {blocked}")
            if row["检查范围"] in ("不适用", "无"):
                self.require(row["说明"] not in ("", "无", "不适用"), "完成", doc.path, f"闸门 {row['检查项']} 不适用有原因")

    def module(self, doc: Document):
        # 模块固定两行元信息位于标题前后皆可，但必须位于第一节前。
        prefix = re.split(r"(?m)^##\s+", doc.text, maxsplit=1)[0]
        status = self.field(doc, "状态", prefix, "完成")
        limitation = self.field(doc, "限制", prefix, "完成")
        self.require(status in STATES, "完成", doc.path, f"模块状态合法：{status}") if status is not None else None
        self.require(limitation in ("无", "有"), "完成", doc.path, f"限制值合法：{limitation}") if limitation is not None else None
        unknowns = self.unresolved(doc)
        section = doc.record_section("候选记录", CANDIDATE_HEADER)
        total = None
        if section is None:
            self.record("失败", "处置", doc.path, "缺少候选记录及固定头部；不能当作零候选")
        else:
            for name in ("扫描范围", "扫描方法", "未检查区域"):
                self.field(doc, name, section, "处置")
            total = self.number(self.field(doc, "检查对象数", section, "处置"), doc, "检查对象数", "处置")
            unscanned = self.field(doc, "未检查区域", section, "处置")
            if unscanned is not None and unscanned != "无":
                self.carried(doc, unknowns, "未检查区域")
        candidates = self.table(doc, "候选记录", CANDIDATE_HEADER, group="处置")
        pending = None
        if candidates is None:
            self.unresolved_complete = False
        if candidates is not None:
            quantities = []
            pending_quantities = []
            for row in candidates:
                source = f"{row['来源位置']} / {row['候选']}"
                quantity = self.number(row["数量"], doc, f"候选 {source} 数量", "处置")
                quantities.append(quantity)
                if quantity is None:
                    self.unresolved_complete = False
                if quantity is not None:
                    self.require(quantity > 0, "处置", doc.path, f"候选 {source} 数量必须为正整数；空集合用空表")
                    if row["处置"] != "琐碎":
                        self.require(quantity == 1, "处置", doc.path, f"候选 {source} 非琐碎项须单独追溯，不能合并数量")
                known_category = self.require(row["类别"] in CATEGORIES, "处置", doc.path, f"候选 {source} 类别合法：{row['类别']}")
                known_disposition = self.require(row["处置"] in DISPOSITIONS, "处置", doc.path, f"候选 {source} 处置合法：{row['处置']}")
                if row["类别"] in CATEGORIES[:7]:
                    self.require(row["处置"] != "琐碎", "处置", doc.path, f"触发类别 {row['类别']} 不得标琐碎：{source}")
                evidence = row["证据或去向"]
                if row["处置"] in ("待核实", "阻塞"):
                    pending_quantities.append(quantity)
                    alt = row["来源位置"]
                    self.carried(doc, unknowns, source, row["处置"], alt)
                elif not known_disposition or not known_category:
                    pending_quantities.append(quantity)
                    self.unresolved_complete = False
                if row["处置"] in ("本文已解释", "模块引用"):
                    refs = links(evidence)
                    # 规范表格示例允许裸 #正文锚点 / 模块路径。
                    if not refs and (evidence.startswith("#") or re.fullmatch(r"[^\s]+\.md(?:#[^\s]+)?", evidence)):
                        refs = [(evidence, evidence)]
                    if not refs:
                        self.unknown("处置", doc.path, f"候选 {source} 去向未能解析为图节点/正文/模块定位")
                    else:
                        for _, raw in refs:
                            target, fragment = self.target(doc, raw)
                            self.require(target is not None and target.is_file(), "处置", doc.path, f"候选 {source} 证据去向实际存在：{raw}")
                            if row["处置"] == "模块引用":
                                self.require(target in self.modules, "处置", doc.path, f"候选 {source} 引用已纳入本知识库的实际模块")
                            elif target != doc.path:
                                self.require(False, "处置", doc.path, f"候选 {source} 本文已解释必须定位当前文档")
                            elif not fragment:
                                self.unknown("处置", doc.path, f"候选 {source} 本文定位未细化到节点/正文")
                            if target and target.is_file() and fragment and target.is_relative_to(self.root):
                                target_doc = self.read(target)
                                if target_doc:
                                    target_info = self.modules.get(target)
                                    if target_info and target_info.get("nodes") is None and fragment not in self.anchors(target_doc):
                                        self.unknown("处置", doc.path, f"候选 {source} 目标节点可能使用未支持 Mermaid 语法：{raw}")
                                    else:
                                        self.require(fragment in self.anchors(target_doc), "处置", doc.path, f"候选 {source} 去向锚点实际存在：{raw}")
                if row["处置"] in ("外部边界", "琐碎"):
                    self.require(evidence not in ("", "无"), "处置", doc.path, f"候选 {source} 有证据或理由文字（真实性须人工核验）")
            if total is not None and all(q is not None for q in quantities):
                self.require(total == sum(quantities), "处置", doc.path, f"检查对象数等于候选数量和：头部 {total} / 行合计 {sum(quantities)}")
            else:
                self.unknown("处置", doc.path, "候选数量汇总未验证；无法解析或缺失的值未当作零")
            if all(q is not None for q in pending_quantities):
                pending = sum(pending_quantities)
        if limitation == "有":
            block = bool(unknowns and any(r["类型"] in ("阻塞", "限制") for r in unknowns))
            explanation = doc.section("限制说明")
            if not block and explanation and explanation.strip() not in ("无", "无。") and not PLACEHOLDER.search(explanation):
                values = doc.fields(explanation)
                detail = all(len(values.get(k, [])) == 1 and values[k][0] not in ("", "无") for k in ("问题", "已尝试方法", "缺失依据", "影响", "重试条件"))
                if not detail:
                    self.unknown("处置", doc.path, "限制说明并非已支持字段写法；必需信息齐备性待人工核验")
                    block = None
                else:
                    block = True
                    self.extra_tasks += 1  # 独立完整限制说明也是一条原始未完成记录。
            if block is not None:
                self.require(block, "完成", doc.path, "限制为有时有对应阻塞项或完整限制说明")
        complete = status in ("本层完成", "已证叶子")
        self.gates(doc, complete, complete)
        if status == "已证叶子":
            self.require(limitation == "无", "完成", doc.path, "已证叶子限制必须为无")
            if pending is None:
                self.unknown("完成", doc.path, "已证叶子未处置数无法确定，不能当作零")
            else:
                self.require(pending == 0, "完成", doc.path, f"已证叶子候选未处置数为 0；实际 {pending}")
            if unknowns is None:
                self.unknown("完成", doc.path, "已证叶子未决明细未解析")
            else:
                self.require(not unknowns, "完成", doc.path, f"已证叶子没有仍未处置的未决/限制项；实际 {len(unknowns)} 行")
        self.modules[doc.path].update(status=status, limitation=limitation, candidates=candidates, unresolved=unknowns, pending=pending)

    def coverage(self, doc: Document) -> dict[str, list | None]:
        unresolved = self.unresolved(doc)
        entries = self.table(doc, "入口", ENTRY_HEADER, group="发现")
        sinks = self.table(doc, "汇点", SINK_HEADER, group="发现")
        methods = self.table(doc, "发现方法", METHOD_HEADER, group="发现")
        crosses = self.table(doc, "交叉复查", CROSS_HEADER, group="发现")
        overview = (self.root / "modules/00-总览.md").resolve()
        overview_info = self.modules.get(overview, {})
        nodes = overview_info.get("nodes")
        for name, rows, prefix in (("入口", entries, "E"), ("汇点", sinks, "S")):
            if rows is not None:
                ids = [r["序号"] for r in rows]
                self.require(len(set(ids)) == len(ids), "发现", doc.path, f"{name}简单序号不重复")
                for row in rows:
                    if not re.fullmatch(prefix + r"[1-9]\d*", row["序号"]):
                        self.unknown("发现", doc.path, f"{name}序号 {row['序号']} 不在 本实现的 {prefix} 加正整数解析写法内；规范的 E1/S1 只是示例")
        for row in entries or []:
            if row["总览节点"] == "未映射":
                self.require(row["下一步"] not in ("", "无"), "发现", doc.path, f"入口 {row['序号']} 未映射有下一步")
                self.carried(doc, unresolved, row["序号"])
                continue
            refs = links(row["总览节点"])
            if not self.require(len(refs) == 1, "发现", doc.path, f"入口 {row['序号']} 指向一个实际总览节点"):
                continue
            _, raw = refs[0]
            target, fragment = self.target(doc, raw)
            self.require(target == overview and bool(fragment), "发现", doc.path, f"入口 {row['序号']} 映射至总览节点定位")
            if nodes is None:
                self.unknown("发现", doc.path, f"入口 {row['序号']} 所指 Mermaid 总览节点未解析")
            else:
                self.require(fragment in nodes, "发现", doc.path, f"入口 {row['序号']} 总览节点 {fragment} 实际存在")
            info_notes = overview_info.get("notes")
            if info_notes is not None:
                matching = [n for n in info_notes if n["节点 ID"] == fragment]
                # 入口序号可以在短注或明确的该节点正文节出现。
                overview_doc = self.docs.get(overview)
                node_text = " ".join(" ".join(n.values()) for n in matching)
                if overview_doc:
                    node_text += " " + (overview_doc.section(fragment) or "")
                if not re.search(r"(?<![A-Za-z0-9])" + re.escape(row["序号"]) + r"(?![A-Za-z0-9])", node_text):
                    self.unknown("发现", doc.path, f"入口 {row['序号']} 未在对应节点短注/以节点ID为题的正文中定位；其他正文写法需人工核验")
            flow_refs = links(row["主体流程"])
            if not flow_refs:
                self.unknown("发现", doc.path, f"入口 {row['序号']} 主体流程没有可解析模块链接")
            else:
                for _, raw in flow_refs:
                    target, _ = self.target(doc, raw)
                    self.require(target in self.modules, "发现", doc.path, f"入口 {row['序号']} 主体流程指向实际模块：{raw}")
        for row in sinks or []:
            position = row["定位或孤立候选"]
            if position in ("孤立候选", "孤立汇点候选", "未映射"):
                self.require(row["下一步"] not in ("", "无"), "发现", doc.path, f"孤立汇点 {row['序号']} 有下一步")
                self.carried(doc, unresolved, row["序号"])
                continue
            refs = links(position)
            if not self.require(bool(refs), "发现", doc.path, f"汇点 {row['序号']} 有候选/正文定位或孤立登记"):
                continue
            located = False
            uncertain = False
            for _, raw in refs:
                target, fragment = self.target(doc, raw)
                if target not in self.modules or not fragment:
                    continue
                target_doc = self.docs[target]
                if fragment == "候选记录":
                    candidates = self.modules[target].get("candidates")
                    if candidates is None:
                        uncertain = True
                    else:
                        located |= any(row["来源位置"] in r["来源位置"] for r in candidates)
                else:
                    body = target_doc.section(fragment)
                    if body is None:
                        # 中文标题原文优先；显式 HTML 锚点只支持到下一个标题。
                        match = re.search(r'<a\s+(?:id|name)=[\"\']' + re.escape(fragment) + r'[\"\'][^>]*>.*?</a>(.*?)(?=\n#{1,6}\s|\Z)', target_doc.text, re.S)
                        body = match.group(1) if match else None
                    if body is not None:
                        located |= row["来源位置"] in body
                    else:
                        uncertain = True
            if located:
                self.record("通过", "发现", doc.path, f"汇点 {row['序号']} 源码位置在所指候选/正文明确出现")
            elif uncertain:
                self.unknown("发现", doc.path, f"汇点 {row['序号']} 目标块无法解析，未把代码可达当映射")
            else:
                self.record("失败", "发现", doc.path, f"汇点 {row['序号']} 没有对应候选/正文中的源码位置：{row['来源位置']}")
        for row in methods or []:
            direction = row["方法或方向"]
            self.require(row["适用性"] in ("适用", "不适用"), "发现", doc.path, f"发现方法 {direction} 适用性明确")
            for field in ("检查对象数", "新增候选数"):
                self.number(row[field], doc, f"发现方法 {direction} {field}", "发现")
            if row["适用性"] == "不适用":
                self.require(row["说明"] not in ("", "无", "不适用"), "发现", doc.path, f"发现方法 {direction} 不适用有原因")
            if row["未检查区域"] != "无":
                self.carried(doc, unresolved, direction)
        for row in crosses or []:
            for field in ("检查对象数", "新增候选数"):
                self.number(row[field], doc, f"交叉复查 {row['交叉复查方法或方向']} {field}", "发现")
            if row["未检查区域"] != "无":
                self.carried(doc, unresolved, row["交叉复查方法或方向"])
        # 这两个声明字段仅序列化设计中的结论，不是新的状态系统。
        overall = self.field(doc, "本轮范围整体完成", group="完成")
        convergence = self.field(doc, "本轮发现暂时收敛", group="发现")
        for value, name, group in ((overall, "整体完成", "完成"), (convergence, "暂时收敛", "发现")):
            if value is not None:
                self.require(value in ("是", "否"), group, doc.path, f"{name}声明为是或否")
        self.field(doc, "范围", group="发现")
        self.field(doc, "召回探针", group="发现")
        claimed = overall == "是"
        if convergence == "是" or claimed:
            directions = {r["方法或方向"] for r in methods or []}
            self.require({"正向入口", "反向汇点", "盲区审查"} <= directions, "发现", doc.path, "暂时收敛须登记正向入口、反向汇点、盲区审查及适用性")
            good_cross = any(r["产生候选的方法或方向"] != r["交叉复查方法或方向"]
                             and r["新增候选数"] == "0" for r in crosses or [])
            self.require(good_cross, "发现", doc.path, "暂时收敛须有不同方法或方向且零新增的交叉复查")
        self.gates(doc, claimed, claimed)
        if claimed:
            self.require(convergence == "是", "完成", doc.path, "整体完成前已记录发现暂时收敛")
            records = [unresolved] + [m.get("unresolved") for m in self.modules.values()]
            if self.unresolved_complete and all(r is not None for r in records):
                self.require(not any(records) and self.extra_tasks == 0, "完成", doc.path, "整体完成没有未处置的原始任务或独立限制说明")
            else:
                self.unknown("完成", doc.path, "整体完成的未决尚未完整解析")
            self.require(all(m.get("status") in STATES[1:] and m.get("limitation") == "无"
                             for m in self.modules.values()), "完成", doc.path, "整体完成没有梳理中或受限模块")
            for rows, field in ((entries, "总览节点"), (sinks, "定位或孤立候选")):
                self.require(rows is not None and all(r[field] not in ("未映射", "孤立候选", "孤立汇点候选") for r in rows or []), "完成", doc.path, "整体完成的入口及汇点均已映射")
            for rows in (methods, crosses):
                self.require(rows is not None and all(r["未检查区域"] == "无" for r in rows or []), "完成", doc.path, "整体完成没有未检查区域")
        return dict(entries=entries, sinks=sinks, methods=methods, crosses=crosses, unresolved=unresolved)

    def summary(self, state: Document, coverage: dict):
        statuses = [m.get("status") for m in self.modules.values()]
        for value in STATES:
            self.counts[value + "模块数"] = statuses.count(value) if self.module_inventory_complete and all(s in STATES for s in statuses) else None
        unresolved_sets = [m.get("unresolved") for m in self.modules.values()] + [coverage.get("unresolved")]
        if self.unresolved_complete and all(x is not None for x in unresolved_sets):
            records = [r for rows in unresolved_sets for r in rows]
            self.raw_counts["未决原始行数"] = len(records)
            self.raw_counts["阻塞原始行数"] = sum(r["类型"] == "阻塞" for r in records)
            # 用户对 §5.1 的补充：当前未完成原始任务逐条计数，不按模块/来源去重。
            # 候选表是这些任务的依据/引用；STATE 只是汇总，不另计一份。
            self.counts["待办数"] = len(records) + self.extra_tasks
            self.counts["阻塞数"] = self.raw_counts["阻塞原始行数"]
        else:
            self.counts["待办数"] = self.counts["阻塞数"] = None
            self.raw_counts["未决原始行数"] = self.raw_counts["阻塞原始行数"] = None
        for key, name in (("入口数", "entries"), ("汇点数", "sinks")):
            value = coverage.get(name)
            self.counts[key] = len(value) if value is not None else None
        records = [coverage.get(k) for k in ("entries", "sinks", "methods", "crosses")]
        self.raw_counts["COVERAGE四张登记表原始行数"] = sum(len(x) for x in records) if all(x is not None for x in records) else None
        self.counts["覆盖记录数"] = self.raw_counts["COVERAGE四张登记表原始行数"]
        for key in SUMMARY_KEYS:
            actual = self.number(self.field(state, key, group="汇总"), state, key, "汇总")
            expected = self.counts[key]
            if expected is None:
                reason = "覆盖登记表未能完整解析" if key == "覆盖记录数" else "原始任务记录未能完整派生"
                self.unknown("汇总", state.path, f"{key}：{reason}，不按零处理、不用原始行数替代")
            elif actual is not None:
                self.require(actual == expected, "汇总", state.path, f"{key} 与原始记录一致：STATE {actual} / 派生 {expected}")
        for key in ("当前焦点", "下一步"):
            self.field(state, key, group="汇总")

    def run(self) -> dict:
        if not self.root.is_dir():
            self.record("失败", "记录", self.root, "project-map 目录不存在")
            return self.report()
        for name in ("README.md", "STATE.md", "COVERAGE.md", "modules/00-总览.md"):
            self.read(self.root / name)
        module_paths = sorted((self.root / "modules").rglob("*.md")) if (self.root / "modules").is_dir() else []
        for path in module_paths:
            doc = self.read(path)
            if doc:
                self.modules[doc.path] = {}
            else:
                self.module_inventory_complete = False
                self.unresolved_complete = False
        # 先建立整个模块/节点索引，引用可共享且不存在唯一父模块或固定深度。
        for path in list(self.modules):
            self.modules[path]["nodes"] = self.mermaid(self.docs[path])
        for path in list(self.modules):
            self.module(self.docs[path])
        for path, info in list(self.modules.items()):
            info["notes"] = self.node_notes(self.docs[path], info["nodes"])
        coverage_doc = self.docs.get((self.root / "COVERAGE.md").resolve())
        coverage = self.coverage(coverage_doc) if coverage_doc else {}
        state = self.docs.get((self.root / "STATE.md").resolve())
        if state:
            self.summary(state, coverage)
        for path in sorted(self.root.rglob("*.md")):
            doc = self.read(path)
            if doc:
                self.local_links(doc)
        if any(r["结果"] == "失败" for r in self.results) and any(m.get("status") in STATES[1:] for m in self.modules.values()):
            self.record("失败", "完成", self.root, "存在 check 失败，不得以当前检查支持完成／叶子状态切换；修复后复检")
        return self.report()

    def report(self):
        statuses = [r["结果"] for r in self.results]
        result = "失败" if "失败" in statuses else "未验证" if "未验证" in statuses else "通过"
        groups = {}
        for name in ("记录", "发现", "处置", "节点", "链接", "完成", "汇总"):
            items = [r["结果"] for r in self.results if r["范围"] == name]
            groups[name] = ("失败" if "失败" in items else "未验证" if "未验证" in items else "通过" if items else "未验证")
        return {"机械检查": result, "范围说明": "只检查已支持且实际执行的记录契约，不证明发现完整或源码语义真实", "分项": groups, "派生计数": self.counts, "原始行数（辅助诊断）": self.raw_counts, "检查计数": dict(Counter(statuses)), "明细": self.results, "人工核验（脚本未验证）": MANUAL}


def main(argv=None):
    parser = argparse.ArgumentParser(description="只读检查 ruan-project-reader 2.2.0 的 project-map；不会改状态。")
    parser.add_argument("project_map", type=Path, help="含 README.md / STATE.md / COVERAGE.md / modules 的知识库目录")
    parser.add_argument("--json", action="store_true", help="将报告输出到标准输出；不创建 JSON 状态库")
    args = parser.parse_args(argv)
    checker = Checker(args.project_map)
    try:
        report = checker.run()
    except (OSError, UnicodeError, ValueError) as exc:
        checker.unknown("记录", args.project_map, f"检查未完成：{type(exc).__name__}: {exc}")
        report = checker.report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"机械检查：{report['机械检查']}")
        print(report["范围说明"])
        for name, result in report["分项"].items():
            print(f"  {name}：{result}")
        for result in report["明细"]:
            if result["结果"] != "通过":
                print(f"[{result['结果']}] {result['范围']} · {result['文件']}：{result['说明']}")
        print("派生计数：" + "；".join(f"{k}={v if v is not None else '未验证'}" for k, v in report["派生计数"].items()))
        print("原始行数（辅助诊断）：" + json.dumps(report["原始行数（辅助诊断）"], ensure_ascii=False))
        print("人工核验（脚本未验证，与机械结果分列）：")
        for item in MANUAL:
            print("  - " + item)
    return {"通过": 0, "失败": 1, "未验证": 2}[report["机械检查"]]


if __name__ == "__main__":
    sys.exit(main())
