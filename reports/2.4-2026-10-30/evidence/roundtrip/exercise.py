"""Explicit isolated scenario actions, not an autonomous agent or state engine.
All remote drafts and user replies here are simulated. No production files are edited.
"""
from pathlib import Path
import difflib
import hashlib
import json
import shutil
import sys

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / 'src/tests'))
import test_acceptance as fixture

HERE = Path(__file__).resolve().parent
root = HERE / 'project-map'
p = root / fixture.MODULE
original = (HERE / 'remote-initial.md').read_text(encoding='utf-8')
source = HERE / 'source/fixture.py'
baseline = hashlib.sha256(source.read_bytes()).hexdigest()
log = []


def save(stage, event):
    target = HERE / stage
    shutil.copytree(root, target / 'project-map', dirs_exist_ok=True)
    result = fixture.check.Checker(root).run()
    (target / 'check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (target / 'input.txt').write_text('模拟执行：'+event+'\n', encoding='utf-8')
    log.append({'stage': stage, 'input': event, 'result': result['机械检查']})


def focus(current, next_action):
    state = root / 'STATE.md'
    text = state.read_text(encoding='utf-8')
    import re
    text = re.sub(r'(?m)^当前焦点：.*$', '当前焦点：'+current, text)
    text = re.sub(r'(?m)^下一步：.*$', '下一步：'+next_action, text)
    state.write_text(text, encoding='utf-8')
    fixture.summary(root)


# Local source evidence really executed in this isolated sample.
ns = {}
exec(compile(source.read_text(), str(source), 'exec'), ns)
store = []
try:
    ns['save'](store, 7, False)
    raise AssertionError('expected denial')
except PermissionError:
    assert store == []
assert ns['save'](store, 7, True) == 7 and store == [7]
(HERE/'source-check.json').write_text(json.dumps({'denied': 'PermissionError; store unchanged', 'allowed': 'append and return 7', 'source_sha256': baseline}, indent=2)+'\n')

# Missing denial is a substantive local rejection, despite a remote claim of completeness.
text = original.replace('| 1 | 0 | 0 | 已检查此结构断言 |', '| 1 | 1 | 1 | 拒绝出口缺失，见未决 |')
text = text.replace('## 限制说明', '| fixture.py:2-3 | 待核实 | allowed为False时拒绝且不写入，当前图遗漏 | 补全拒绝节点与边 | 无 | 无 | 无 | 无 |\n\n## 限制说明')
text = text.replace('模拟输入：已收到质疑与完整稿，已逐项比对合成事实。', '已读取source/fixture.py:1-5并执行许可/拒绝分支；当前图缺少第2-3行拒绝路径，本地核验未通过。')
p.write_text(text, encoding='utf-8')
focus('保存模块梳理中，等待完整修订稿', '收到拒绝出口修订后重做本层适用核验')
(HERE/'local-feedback.md').write_text('''# 本地转交说明（隔离模拟）

~~~~text
当前稿的执行图只有保存→返回，缺source/fixture.py:2-3：allowed为False时抛PermissionError，且第4行append不发生。本地已执行两个分支确认。请补条件、拒绝出口、短注及相应候选，提交完整UTF-8 Markdown文件。当前状态梳理中，修改范围为保存模块。本地将再次核验，不能用“内容完整”替代源码依据。
~~~~
''', encoding='utf-8')
save('01-local-rejected', '远端声称完整，但源码存在重要拒绝出口。')

# Synthetic remote file is explicitly authored as test input, then transferred byte-for-byte.
revision = original.replace('合成夹具的单次保存与返回。', 'allowed为真时向store追加value并返回；为假时抛PermissionError，store不变。')
revision = revision.replace('  A["保存"]\n  B["返回"]\n  A --> B', '  Q{"允许写入"}\n  A["保存"]\n  B["返回"]\n  D["拒绝"]\n  Q -->|是| A\n  Q -->|否| D\n  A --> B')
revision = revision.replace('| A | 保存 |', '| Q | 允许写入 | 以allowed布尔值决定 | 无 |\n| D | 拒绝 | 抛PermissionError且不写入 | 无 |\n| A | 保存 |')
revision = revision.replace('fixture.py:save 写入后返回。此为测试构造的事实。', 'fixture.py:save 在第2-3行检查allowed，为假抛PermissionError；通过后第4行store.append(value)，第5行返回value。本轮无外部运行配置。')
revision = revision.replace('检查对象数：1', '检查对象数：3')
revision = revision.replace('| fixture.py:save | 保存记录', '| fixture.py:2 | 许可条件 | 权限判断算法 | 1 | 本文已解释 | [规则](#规则) |\n| fixture.py:3 | 拒绝出口 | 异常重试补偿 | 1 | 本文已解释 | [规则](#规则) |\n| fixture.py:save | 保存记录')
revision = revision.replace('模拟输入：已收到质疑与完整稿，已逐项比对合成事实。', '模拟远端质疑与完整文件已收到；source/fixture.py:1-5和许可/拒绝分支实测见外部验收证据。候选条件、写入、拒绝已逐项核实；叶子无未落实的重要阶段。完整Mermaid渲染未验证，节点和边已人工比对。')
(HERE/'remote-revised.md').write_text(revision, encoding='utf-8')
(HERE/'local-revision.diff').write_text(''.join(difflib.unified_diff(p.read_text().splitlines(True),revision.splitlines(True),fromfile='current',tofile='received-file')),encoding='utf-8')
shutil.copyfile(HERE/'remote-revised.md',p)
assert p.read_bytes() == (HERE/'remote-revised.md').read_bytes()
digest = fixture.record(p,'待验收','未取得','source/fixture.py SHA-256 '+baseline+'；无外部配置；许可/拒绝分支实际执行，本文件四项闸门与候选已核对')
focus('保存.md '+digest[:10]+' 待用户验收', '等待当前版本单一验收回答，不启动下一协作单位')
save('02-pending', '完整修订文件已收到并适用核验通过；尚无用户回答。')
before={x.relative_to(root):x.read_bytes() for x in root.rglob('*') if x.is_file()}
for _ in range(2):
    fixture.check.Checker(root).run()
assert before == {x.relative_to(root):x.read_bytes() for x in root.rglob('*') if x.is_file()}
save('03-no-new-input', '两次只读检查，没有新材料或用户决定，保持全部文件及待验收状态。')

# Apply a conditional response as a revision request; no language-parser heuristic.
p.write_text(p.read_text().replace('状态：待验收','状态：梳理中').replace('用户验收回答：未取得','用户验收回答：模拟用户：可以，但请把图改为从左到右。'),encoding='utf-8')
focus('保存模块梳理中，等待远端表达修订', '转交图方向意见；完整新稿回来后对照节点、边、条件、出口及短注')
save('04-conditional-response','可以，但请把图改为从左到右。属于修改异议，未转正。')
layout=p.read_text().replace('flowchart TD','flowchart LR')
(HERE/'remote-layout.md').write_text(layout,encoding='utf-8')
diff=''.join(difflib.unified_diff(p.read_text().splitlines(True),layout.splitlines(True),fromfile='current',tofile='received-layout'))
(HERE/'local-layout.diff').write_text(diff,encoding='utf-8')
assert '-flowchart TD' in diff and '+flowchart LR' in diff
shutil.copyfile(HERE/'remote-layout.md',p)
new=fixture.record(p,'待验收','未取得','source/fixture.py SHA-256 '+baseline+'；无外部配置；方向调整的节点/边/条件/出口/短注/引用比对一致，沿用技术核验')
assert digest != new
focus('保存.md '+new[:10]+' 待用户验收', '等待新稿验收；无继续授权')
save('05-layout-pending','新稿只有图方向变化；自行diff并核对语义，不重查全仓，重新等待新版本认可。')

# Record discovery while waiting without silently opening a new unit.
c=root/'COVERAGE.md'
coverage=c.read_text().replace('本轮发现暂时收敛：是','本轮发现暂时收敛：否')
line='| E1 | fixture.py:save | [保存](modules/保存.md) | [保存流程](modules/00-总览.md#F) | 无 |'
coverage=coverage.replace(line,line+'\n| E2 | 模拟新线索：其他入口 | 未展开 | 未映射 | 后续授权后核实归属 |')
coverage += '\n| E2 | 待核实 | 新入口线索待核实，与当前保存事实无已知冲突 | 后续授权后核实归属 | 无 | 无 | 无 | 无 |\n'
c.write_text(coverage,encoding='utf-8')
fixture.summary(root)
assert fixture.check.fingerprint(p)['sha256']==new and '状态：待验收' in p.read_text()
save('06-discovery-while-waiting','模拟已发现无关入口线索，立即登记COVERAGE和未决，不展开下一模块，不改当前读者稿。')

p.write_text(p.read_text().replace('状态：待验收','状态：已证叶子').replace('用户验收回答：未取得','用户验收回答：模拟用户：通过当前保存.md。'),encoding='utf-8')
focus('保存.md当前版本已验收，等待继续授权','仅认可当前稿，未授权启动下一项')
save('07-accepted-waiting-continue','通过当前保存.md。只认可当前稿，没有继续指令。')
assert len(list((root/'modules').glob('*.md')))==2
focus('保存.md已验收；用户明确允许下一项','模拟用户：本稿通过，开始下一项；仅此下一项，待选具体对象')
save('08-explicit-next','本稿通过，开始下一项。分别记录认可和一次继续指令；本演练不再实际启动后续阅读。')

assert hashlib.sha256(source.read_bytes()).hexdigest()==baseline
(HERE/'events.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'events':len(log),'source_unchanged':True,'fingerprint_before_layout':digest,'fingerprint_after_layout':new,'boundary':'模拟用户/远端与手工流程应用；未测试真实Goal、独立代理停止或真实双AI往返'},ensure_ascii=False,indent=2))
