"""2.4 executable contracts; all approvals in these tests are simulated inputs."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import unittest

from test_check import BASE, SCRIPT, MODULE, OVERVIEW, check


def current_module(text):
    # Upgrade only isolated synthetic input; historical fixtures stay byte-identical.
    text = text.replace('## 规则', '## 必要规则与源码依据\n\n<a id="规则"></a>')
    text = text.replace('## 候选记录', '## 下钻、引用与外部去向\n\n沿图中引用继续阅读。\n\n## 候选记录')
    return text + '\n## 限制说明\n\n无\n\n## 核验与下一步\n\n模拟输入：已收到质疑与完整稿，已逐项比对合成事实。\n'


def record(path, state='待验收', answer='未取得', baseline='合成事实及本文件闸门记录；模拟本地核验'):
    text = path.read_text(encoding='utf-8').split('\n## 验收记录', 1)[0]
    proposed = '本层完成' if path.name.startswith('00-') else '已证叶子'
    text = re.sub(r'(?m)^状态：.*$', '状态：' + state, text)
    path.write_text(text, encoding='utf-8')
    digest = check.fingerprint(path)['sha256']
    text += f'\n## 验收记录\n\n拟完成类型：{proposed}\n读者内容指纹：{digest}\n核验基准：{baseline}\n用户验收问题：是否认可 {path.name}（{digest[:10]}）当前版本？限制无；未验证真实平台行为。\n用户验收回答：{answer}\n'
    path.write_text(text, encoding='utf-8')
    return digest


def summary(root):
    report = check.Checker(root).run()
    path = root / 'STATE.md'
    text = path.read_text(encoding='utf-8')
    for key, val in report['派生计数'].items():
        text = re.sub(r'(?m)^' + key + '：.*$', f'{key}：{val}', text)
    path.write_text(text, encoding='utf-8')


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='reader 2.4 中文 ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project-map'
        shutil.copytree(BASE / 'fixtures/valid-map', self.root)
        for p in (self.root / 'modules').glob('*.md'):
            p.write_text(current_module(p.read_text(encoding='utf-8')), encoding='utf-8')
        state = self.root / 'STATE.md'
        state.write_text(state.read_text(encoding='utf-8') + '\n规范版本：2.4\n待验收模块数：2\n', encoding='utf-8')
        coverage = self.root / 'COVERAGE.md'
        coverage.write_text(coverage.read_text(encoding='utf-8').replace('本轮范围整体完成：是', '本轮范围整体完成：否'), encoding='utf-8')

    def prepare(self, accepted=False):
        for p in (self.root / 'modules').glob('*.md'):
            state = ('本层完成' if p.name.startswith('00-') else '已证叶子') if accepted else '待验收'
            record(p, state, '模拟用户：通过当前文件。' if accepted else '未取得')
        summary(self.root)

    def test_fingerprint_is_read_only(self):
        p = self.root / MODULE
        before = p.read_bytes()
        result = check.fingerprint(p)
        self.assertEqual(result['结果'], '通过', result)
        self.assertRegex(result['sha256'], r'^[0-9a-f]{64}$')
        self.assertEqual(before, p.read_bytes())

    def test_pending_and_missing_approval(self):
        self.prepare()
        self.assertEqual(check.Checker(self.root).run()['机械检查'], '通过')
        p = self.root / MODULE
        p.write_text(p.read_text().replace('状态：待验收', '状态：已证叶子'))
        summary(self.root)
        self.assertEqual(check.Checker(self.root).run()['分项']['验收'], '失败')

    def replace(self, relative, old, new):
        path = self.root / relative
        text = path.read_text(encoding='utf-8')
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding='utf-8')

    def scope_record(self, answer='未取得', claimed=False):
        value = check.scope_fingerprint(self.root)
        self.assertEqual(value['结果'], '通过', value)
        p = self.root / 'COVERAGE.md'
        text = p.read_text(encoding='utf-8').split('\n## 整体验收记录', 1)[0]
        text = re.sub(r'本轮范围整体完成：[是否]', '本轮范围整体完成：' + ('是' if claimed else '否'), text)
        text += f"\n## 整体验收记录\n\n整体读者内容指纹：{value['sha256']}\n技术核验：合成记录全项目四项闸门已核对\n用户验收问题：是否认可清单中整组交付（{value['sha256'][:10]}），覆盖与全项目闸门按所列证据？\n用户验收回答：{answer}\n\n| 模块路径 |\n| --- |\n"
        text += ''.join('| ' + item['路径'] + ' |\n' for item in value['清单'])
        p.write_text(text, encoding='utf-8')
        return value

    def test_normalization_and_independent_golden_bytes(self):
        p = self.root / MODULE
        original = p.read_bytes()
        digest = check.fingerprint(p)['sha256']
        p.write_bytes(b'\xef\xbb\xbf' + original.replace(b'\n', b'\r\n'))
        self.assertEqual(check.fingerprint(p)['sha256'], digest)
        p.write_bytes(original.replace(b'\n## ', b'\n\n\n## ') + b'\n\n')
        self.assertEqual(check.fingerprint(p)['sha256'], digest)
        # Fixed tiny reader payload: independently specified expected bytes.
        headings = ['职责与边界', '执行图', '逐节点短注', '必要规则与源码依据', '下钻、引用与外部去向']
        reader = '# 样例\n限制：无\n\n' + '\n\n'.join('## ' + h + '\n\n正文  原样' for h in headings) + '\n'
        full = reader.replace('# 样例\n', '# 样例\n状态：梳理中\n')
        full += '\n' + '\n\n'.join('## ' + h + '\n\n操作记录' for h in ['候选记录','未决','限制说明','核验与下一步'])
        p.write_text(full, encoding='utf-8')
        self.assertEqual(check.fingerprint(p)['sha256'], hashlib.sha256(reader.encode('utf-8')).hexdigest())
        p.write_bytes(p.read_bytes().replace(b'\n', b'\r', 1))
        self.assertEqual(check.fingerprint(p)['结果'], '未验证')
        self.assertIsNone(check.fingerprint(p)['sha256'])
        p.write_bytes(b'\xff')
        self.assertEqual(check.fingerprint(p)['结果'], '未验证')

    def test_reader_changes_invalidate_and_operational_changes_do_not(self):
        self.prepare(True)
        p = self.root / MODULE
        original = p.read_text(encoding='utf-8')
        digest = check.fingerprint(p)['sha256']
        for section in check.EXCLUDED_SECTIONS:
            with self.subTest(section=section):
                text = original.replace('## ' + section + '\n', '## ' + section + '\n\n调查已推进。\n')
                p.write_text(text, encoding='utf-8')
                self.assertEqual(check.fingerprint(p)['sha256'], digest)
        for old, new in [('状态：已证叶子','状态：待验收')]:
            p.write_text(original.replace(old,new), encoding='utf-8')
            self.assertEqual(check.fingerprint(p)['sha256'], digest)
        for old,new in [('限制：无','限制：有'), ('A --> B','A -.-> B'), ('写入记录后返回结果','写入后返回标识'), ('fixture.py:save 写入后返回','fixture.py:save 可能失败'), ('# 保存','# 保存\n前置重要未知'), ('# 保存','标题前的重要事实\n# 保存')]:
            with self.subTest(change=new):
                p.write_text(original.replace(old,new),encoding='utf-8')
                self.assertNotEqual(check.fingerprint(p)['sha256'],digest)
        p.write_text(original+'\n## 补充\n新事实\n',encoding='utf-8')
        self.assertNotEqual(check.fingerprint(p)['sha256'],digest)
        self.assertEqual(check.Checker(self.root).run()['分项']['验收'],'失败')

    def test_fences_and_headings_follow_markdown_boundaries(self):
        p=self.root/MODULE
        original=p.read_text(encoding='utf-8')
        for char,length,closing,indent in [('`',3,3,0),('`',4,5,3),('~',3,4,2),('~',5,6,0)]:
            with self.subTest(char=char,length=length):
                body=' '*indent+char*length+'text\n## 未决\n# 非标题\n'+char*(length-1)+'\n'+char*closing+'   \n'
                p.write_text(original.replace('## 职责与边界\n', '## 职责与边界\n\n'+body),encoding='utf-8')
                good=check.fingerprint(p)
                self.assertEqual(good['结果'],'通过',good)
                p.write_text(p.read_text().replace('# 非标题','# 内容改变'),encoding='utf-8')
                self.assertNotEqual(check.fingerprint(p)['sha256'],good['sha256'])
        p.write_text(original.replace('## 职责与边界','   ## 职责与边界 ###'),encoding='utf-8')
        self.assertEqual(check.fingerprint(p)['结果'],'通过')
        p.write_text(original+'\n## 补充\n    ## 未决\n',encoding='utf-8')
        self.assertEqual(check.fingerprint(p)['结果'],'通过')
        for ending in ['\n```text\n## 未决\n', '\n~~~~text\n~~~\n', '\n```\n~~~~\n']:
            p.write_text(original+ending,encoding='utf-8')
            self.assertEqual(check.fingerprint(p)['结果'],'未验证')
            self.assertIsNone(check.fingerprint(p)['sha256'])
        # Backtick-containing info string is not an opening fence.
        p.write_text(original+'\n```bad`info\n## 补充\n事实\n',encoding='utf-8')
        self.assertEqual(check.fingerprint(p)['结果'],'通过')

    def test_no_partial_hash_on_ambiguous_or_missing_structure(self):
        p=self.root/MODULE
        original=p.read_text(encoding='utf-8')
        cases=[(original+'\n## 未决\n无\n','未验证'),(original+'\n## 验收记录\n无\n## 验收记录\n无\n','未验证'),(original.replace('## 职责与边界','## 边界'),'失败'),(original.replace('状态：已证叶子','状态：已证叶子\n状态：已证叶子'),'失败'),(original.replace('限制：无','限制：有时'),'失败'),(original.replace('限制：无',''),'失败'),(original+'\n# 第二标题\n','失败')]
        for body,expected in cases:
            with self.subTest(expected=expected,body=body[-35:]):
                p.write_text(body,encoding='utf-8')
                r=check.fingerprint(p)
                self.assertEqual(r['结果'],expected,r)
                self.assertIsNone(r['sha256'])

    def test_body_is_not_unicode_normalized_or_whitespace_folded(self):
        p=self.root/MODULE
        original=p.read_text(encoding='utf-8')
        p.write_text(original+'\n## 补充\ncafé  a\n',encoding='utf-8')
        digest=check.fingerprint(p)['sha256']
        p.write_text(unicodedata.normalize('NFD',p.read_text()),encoding='utf-8')
        self.assertNotEqual(check.fingerprint(p)['sha256'],digest)
        p.write_text(original+'\n## 补充\ncafé a\n',encoding='utf-8')
        self.assertNotEqual(check.fingerprint(p)['sha256'],digest)

    def test_new_contract_cannot_be_bypassed_by_deleting_version(self):
        self.prepare()
        self.replace('STATE.md','规范版本：2.4','')
        self.assertEqual(check.Checker(self.root).run()['分项']['规范'],'失败')
        self.replace('STATE.md','待验收模块数：2','')
        self.assertEqual(check.Checker(self.root).run()['分项']['规范'],'失败')

    def test_declared_contract_requires_records_and_nine_counts(self):
        self.prepare()
        self.replace('STATE.md','待验收模块数：2','')
        self.assertEqual(check.Checker(self.root).run()['分项']['汇总'],'失败')
        self.replace(MODULE,'## 验收记录','## 其他记录')
        self.assertEqual(check.Checker(self.root).run()['分项']['验收'],'失败')

    def test_unknown_fingerprint_prevents_promotion_even_with_answer(self):
        self.prepare()
        p=self.root/MODULE
        digest=check.fingerprint(p)['sha256']
        self.replace(MODULE,'读者内容指纹：'+digest,'读者内容指纹：未验证')
        self.replace(MODULE,'用户验收回答：未取得','用户验收回答：模拟用户：通过')
        self.assertEqual(check.Checker(self.root).run()['机械检查'],'未验证')
        self.replace(MODULE,'状态：待验收','状态：已证叶子')
        summary(self.root)
        self.assertEqual(check.Checker(self.root).run()['分项']['验收'],'失败')

    def test_each_file_approval_and_partial_batch(self):
        self.prepare()
        record(self.root/OVERVIEW,'本层完成','模拟用户会话T：仅认可00-总览.md。')
        summary(self.root)
        report=check.Checker(self.root).run()
        self.assertEqual(report['机械检查'],'通过',report['明细'])
        self.assertEqual(report['派生计数']['待验收模块数'],1)
        self.assertEqual(report['派生计数']['本层完成模块数'],1)
        self.assertNotIn(check.fingerprint(self.root/MODULE)['sha256'],(self.root/OVERVIEW).read_text())
        record(self.root/MODULE,'已证叶子','模拟用户会话U：认可保存.md。')
        summary(self.root)
        self.assertEqual(check.Checker(self.root).run()['机械检查'],'通过')

    def test_nonblocking_problems_preserve_parent_completion(self):
        self.prepare(True)
        self.replace(OVERVIEW,'| 1 | 0 | 0 | 已检查此结构断言 |','| 1 | 1 | 0 | 子层已承接，不影响本层边界 |')
        self.assertEqual(check.Checker(self.root).run()['机械检查'],'通过')
        self.replace(OVERVIEW,'| 1 | 1 | 0 |','| 1 | 1 | 1 |')
        self.assertEqual(check.Checker(self.root).run()['分项']['完成'],'失败')

    def test_pending_leaf_still_requires_technical_gates(self):
        self.prepare()
        self.replace(MODULE,'| 1 | 0 | 0 | 已检查此结构断言 |','| 1 | 1 | 1 | 出口未核实 |')
        self.assertEqual(check.Checker(self.root).run()['分项']['完成'],'失败')
        self.replace(MODULE,'| 1 | 1 | 1 | 出口未核实 |','| 1 | 0 | 0 | 已检查此结构断言 |')
        self.replace(MODULE,'限制：无','限制：有')
        self.assertEqual(check.Checker(self.root).run()['分项']['完成'],'失败')

    def test_scope_requires_individual_acceptance_then_own_answer(self):
        self.prepare()
        self.scope_record('模拟用户：整组通过',True)
        self.assertEqual(check.Checker(self.root).run()['分项']['验收'],'失败')
        self.prepare(True)
        self.scope_record()
        self.assertEqual(check.Checker(self.root).run()['机械检查'],'通过')
        self.replace('COVERAGE.md','本轮范围整体完成：否','本轮范围整体完成：是')
        self.assertEqual(check.Checker(self.root).run()['分项']['验收'],'失败')
        self.scope_record('模拟用户：认可整体覆盖、清单与交付版本。',True)
        self.assertEqual(check.Checker(self.root).run()['机械检查'],'通过')

    def test_scope_path_rules_and_independent_recalculation(self):
        self.prepare(True)
        for name in ['é','z','汉']:
            shutil.copyfile(self.root/MODULE,self.root/'modules'/f'{name}.md')
        r=check.scope_fingerprint(self.root)
        self.assertEqual(r['结果'],'通过')
        expected_names=['modules/00-总览.md','modules/z.md','modules/é.md','modules/保存.md','modules/汉.md']
        self.assertEqual([x['路径'] for x in r['清单']],expected_names)
        payload=b''.join(name.encode()+b'\0'+check.fingerprint(self.root/name)['sha256'].encode()+b'\n' for name in expected_names)
        self.assertEqual(r['sha256'],hashlib.sha256(payload).hexdigest())
        self.assertEqual(check.scope_fingerprint(self.root,[x.replace('/','\\') for x in expected_names])['sha256'],r['sha256'])
        nfd=self.root/'modules'/('e\u0301.md')
        (self.root/'modules/é.md').rename(nfd)
        self.assertEqual(check.scope_fingerprint(self.root)['sha256'],r['sha256'])
        for paths in [expected_names[:-1],expected_names+['modules/z.md'],expected_names+['README.md'],['../escape.md'],expected_names+[str(self.root/MODULE)]]:
            bad=check.scope_fingerprint(self.root,paths)
            self.assertEqual(bad['结果'],'失败',bad)
            self.assertIsNone(bad['sha256'])
        shutil.copyfile(nfd,self.root/'modules/é.md')
        self.assertEqual(check.scope_fingerprint(self.root)['结果'],'失败')

    def test_scope_detects_rename_add_remove_and_changed_reader(self):
        self.prepare(True)
        original=check.scope_fingerprint(self.root)['sha256']
        path=self.root/MODULE
        path.rename(path.with_name('新名称.md'))
        self.assertNotEqual(check.scope_fingerprint(self.root)['sha256'],original)
        path.with_name('新名称.md').rename(path)
        self.assertEqual(check.scope_fingerprint(self.root)['sha256'],original)
        self.scope_record('模拟用户：通过',True)
        self.replace('COVERAGE.md','| modules/保存.md |','')
        self.assertEqual(check.Checker(self.root).run()['分项']['验收'],'失败')
        proc=subprocess.run([sys.executable,str(SCRIPT),'--scope-fingerprint',str(self.root)],capture_output=True,text=True)
        self.assertEqual(proc.returncode,1)
        self.assertIsNone(json.loads(proc.stdout)['sha256'])

    def test_cli_hashes_match_normal_check_and_are_read_only(self):
        self.prepare(True)
        self.scope_record('模拟用户：通过',True)
        def snapshot():
            return {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
        before=snapshot()
        computed=check.Checker(self.root).run()['读者内容指纹'][MODULE]['sha256']
        for args in [['--fingerprint',str(self.root/MODULE)],['--scope-fingerprint',str(self.root)],[str(self.root),'--json']]:
            proc=subprocess.run([sys.executable,str(SCRIPT),*args],capture_output=True,text=True,cwd=self.tmp.name)
            self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
            r=json.loads(proc.stdout)
            if args[0]=='--fingerprint':
                self.assertEqual(r['sha256'],computed)
            self.assertEqual(snapshot(),before)
        with (self.root/MODULE).open('a',encoding='utf-8') as f:
            f.write('\n~~~~\n## 未决\n')
        proc=subprocess.run([sys.executable,str(SCRIPT),'--fingerprint',str(self.root/MODULE)],capture_output=True,text=True)
        self.assertEqual(proc.returncode,2)
        self.assertIsNone(json.loads(proc.stdout)['sha256'])

    def test_source_baseline_unknown_is_explicit_not_fabricated(self):
        self.prepare()
        record(self.root/MODULE,'待验收','未取得','基准未知；沿用既有技术核验记录，未重新读取源码；依据本文件闸门记录')
        self.assertEqual(check.Checker(self.root).run()['机械检查'],'通过')
        self.assertIn('基准未知',(self.root/MODULE).read_text())

    def test_active_empty_scope_is_not_silently_replaced_with_inventory(self):
        self.prepare(True)
        self.scope_record('模拟用户：通过',True)
        self.replace('COVERAGE.md','| modules/保存.md |','')
        self.replace('COVERAGE.md','| modules/00-总览.md |','')
        proc=subprocess.run([sys.executable,str(SCRIPT),'--scope-fingerprint',str(self.root)],capture_output=True,text=True)
        self.assertEqual(proc.returncode,1,proc.stdout)
        self.assertIsNone(json.loads(proc.stdout)['sha256'])

    def test_unreadable_completed_module_is_unverified_not_false_fail(self):
        self.prepare(True)
        self.scope_record('模拟用户：通过',True)
        (self.root/MODULE).write_bytes(b'\xff')
        result=check.Checker(self.root).run()
        self.assertEqual(result['机械检查'],'未验证',[r for r in result['明细'] if r['结果']=='失败'])

    def evidence(self, name, event):
        destination=os.environ.get('READER_EVIDENCE_DIR')
        if destination:
            target=Path(destination)/name
            target.mkdir(parents=True,exist_ok=True)
            shutil.copytree(self.root,target/'project-map',dirs_exist_ok=True)
            report=check.Checker(self.root).run()
            (target/'check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            (target/'input.txt').write_text('隔离模拟输入；不代表真实用户/远端或平台Goal。\n'+event+'\n',encoding='utf-8')

    def test_scope_revocation_persists_when_hash_returns(self):
        self.prepare(True)
        accepted=self.scope_record('模拟用户：认可当前整体交付',True)['sha256']
        self.evidence('scope-1-accepted','A/B分别通过，随后明确认可整体交付。')
        original=(self.root/MODULE).read_text(encoding='utf-8')
        # Execute the documented reopen action on the actual isolated files.
        self.replace(MODULE,'状态：已证叶子','状态：梳理中')
        coverage=self.root/'COVERAGE.md'
        body=coverage.read_text(encoding='utf-8').split('\n## 整体验收记录',1)[0].replace('本轮范围整体完成：是','本轮范围整体完成：否')
        empty='\n## 整体验收记录\n\n整体读者内容指纹：未取得\n技术核验：未取得\n用户验收问题：未取得\n用户验收回答：未取得\n\n| 模块路径 |\n| --- |\n'
        coverage.write_text(body+empty,encoding='utf-8')
        self.replace(MODULE,'fixture.py:save 写入后返回','fixture.py:save 的成功条件需要再次核对')
        summary(self.root)
        self.evidence('scope-2-reopened','新证据实质影响保存模块；先回梳理中，同步撤销整体声明及有效记录。')
        self.assertIn('本轮范围整体完成：否',coverage.read_text())
        self.assertIn('整体读者内容指纹：未取得',coverage.read_text())
        # Restore the old reader bytes, keeping the workflow in reopened state.
        (self.root/MODULE).write_text(original.replace('状态：已证叶子','状态：梳理中'),encoding='utf-8')
        self.assertEqual(check.scope_fingerprint(self.root)['sha256'],accepted)
        before={p:p.read_bytes() for p in self.root.rglob('*.md')}
        for _ in range(2):
            check.Checker(self.root).run()
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*.md')})
        self.assertIn('本轮范围整体完成：否',coverage.read_text())
        self.evidence('scope-3-hash-restored','模拟中断恢复：正文恢复旧哈希；没有新验收输入，保持梳理中/整体否。')
        record(self.root/MODULE,'待验收')
        summary(self.root)
        self.evidence('scope-4-pending','适用复核完成，重新等待具体版本验收。')
        record(self.root/MODULE,'已证叶子','模拟用户：认可保存.md当前版本。')
        summary(self.root)
        self.assertIn('本轮范围整体完成：否',coverage.read_text())
        self.evidence('scope-5-individual-only','模块重新认可不等于重新认可整体。')
        # A new explicit overall acceptance precedes the coverage-only change.
        self.scope_record('模拟用户：重新认可当前整体版本。',True)
        self.evidence('scope-6-overall-renewed','模块及整体分别重新认可。')
        # A coverage conclusion can change without changing any module hash.
        body=coverage.read_text().split('\n## 整体验收记录',1)[0].replace('本轮范围整体完成：是','本轮范围整体完成：否').replace('范围：测试构造的保存流程','范围：测试构造的保存流程；有效配置需再次核实')
        coverage.write_text(body+empty,encoding='utf-8')
        self.assertEqual(check.scope_fingerprint(self.root)['sha256'],accepted)
        self.assertIn('本轮范围整体完成：否',coverage.read_text())
        self.evidence('scope-7-coverage-change','覆盖依据变化，整体持续否，不能用不变哈希替代技术复核。')

    def test_explicit_whole_library_migration_and_partial_acceptance(self):
        shutil.rmtree(self.root)
        shutil.copytree(BASE/'fixtures/valid-map',self.root)
        before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*.md')}
        old=check.Checker(self.root).run()
        self.assertEqual(old['机械检查'],'未验证')
        self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*.md')})
        self.evidence('migration-1-read-only','没有迁移指令；只读检查后保持全部字节。')
        # Simulated explicit instruction, not inferred from installation or check.
        instruction='模拟用户：已在知识库外备份；请按2.4对整个知识库调整格式，基准是否变化无法确认。'
        original_types={p:p.read_text().split('状态：')[1].split('\n')[0] for p in (self.root/'modules').glob('*.md')}
        candidates={p:p.read_text().split('## 候选记录',1)[1].split('## 闸门记录',1)[0] for p in original_types}
        for p in original_types:
            p.write_text(current_module(p.read_text(encoding='utf-8')),encoding='utf-8')
            record(p,'待验收','未取得','基准未知；沿用既有技术核验记录，未重新读取源码；依据本文件闸门记录')
            text=p.read_text().replace('当前版本？','当前版本？无法证明当前源码与既有核验时一致，是否接受既有技术成果的此项不确定性？')
            p.write_text(text,encoding='utf-8')
        self.replace('COVERAGE.md','本轮范围整体完成：是','本轮范围整体完成：否')
        state=self.root/'STATE.md'
        state.write_text(state.read_text()+'\n规范版本：2.4\n待验收模块数：2\n',encoding='utf-8')
        summary(self.root)
        result=check.Checker(self.root).run()
        self.assertEqual(result['机械检查'],'通过',result['明细'])
        for p,proposed in original_types.items():
            self.assertIn('拟完成类型：'+proposed,p.read_text())
            self.assertEqual(p.read_text().split('## 候选记录',1)[1].split('## 闸门记录',1)[0],candidates[p])
        self.evidence('migration-2-whole-pending',instruction)
        self.replace(OVERVIEW,'状态：待验收','状态：本层完成')
        self.replace(OVERVIEW,'用户验收回答：未取得','用户验收回答：模拟用户：仅认可总览当前版本，接受基准未知，不将此视为当前源码一致；等待继续。')
        summary(self.root)
        result=check.Checker(self.root).run()
        self.assertEqual(result['机械检查'],'通过',result['明细'])
        self.assertEqual(result['派生计数']['待验收模块数'],1)
        self.assertIn('本轮范围整体完成：否',(self.root/'COVERAGE.md').read_text())
        self.evidence('migration-3-partial','模拟用户仅认可总览，其余仍待验收，整体否；没有继续授权。')
        # Known relevant change cannot be accepted using the historical basis.
        self.replace(MODULE,'状态：待验收','状态：梳理中')
        self.replace(MODULE,'核验基准：基准未知；','核验基准：已知相关配置变化待补证；')
        summary(self.root)
        self.assertEqual(check.Checker(self.root).run()['派生计数']['梳理中模块数'],1)
        self.evidence('migration-4-known-change','模拟用户声明保存条件的有效配置已变；保存模块先回梳理中等待受影响核验。')

    def test_file_transfer_equivalence_and_detectable_truncation(self):
        original=(self.root/MODULE).read_bytes()
        incoming=Path(self.tmp.name)/'incoming.md'
        incoming.write_bytes(original)
        staging=Path(self.tmp.name)/'staged.md'
        shutil.copyfile(incoming,staging)
        self.assertEqual(incoming.read_bytes(),staging.read_bytes())
        # Paste transport is tested as raw text, not model reconstruction.
        pasted=Path(self.tmp.name)/'pasted.md'
        pasted.write_text(original.decode('utf-8'),encoding='utf-8')
        self.assertEqual(pasted.read_bytes(),staging.read_bytes())
        pasted.write_bytes(original[:-30])
        self.assertNotEqual(hashlib.sha256(pasted.read_bytes()).hexdigest(),hashlib.sha256(incoming.read_bytes()).hexdigest())
        self.assertNotEqual(pasted.read_bytes(),incoming.read_bytes())

if __name__ == '__main__':
    unittest.main()
