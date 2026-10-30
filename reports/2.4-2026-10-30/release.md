# 2.4 发布记录

日期：2026-10-30（Asia/Singapore）。**正式成品已交付：2.4 / 2.4.0。**

目标设计为 `design/versions/2.4.0.md`（approved，previous_version=2.3.0），正式发布清单 `install/.release.json` 为2.4.0。用户在收到完整验收报告与未验证范围后明确答复：“允许，交付后推送到远端”。该许可用于正式交付、提交和推送，不改变验收项目的证据等级，也不包含Tag或GitHub Release。

## 交付内容与验证

- 正式安装目录：`install/ruan-project-reader/`，14个运行文件。
- 正式安装包：`install/ruan-project-reader.zip`，从本次正式安装目录生成。
- 发布清单：`install/.release.json`，由原构建器生成。
- 主仓库 `python3 src/build_release.py --build` 退出0，重跑59项回归通过，证据 `release-build.txt`。
- 主仓库 `python3 src/build_release.py --verify` 退出0，证据 `release-verify.txt`。
- 正式安装包14个成员与正式成品、开发源逐字节相同；Skill Creator校验和安装版check实际运行通过，证据 `release-validation.json`、`release-skill-validation.txt`、`release-installed-check.json`。
- 正式成品无痕检查无命中，当前版本一致性见 `release-no-trace-grep.txt`、`release-version-audit.json`。

| 校验项 | SHA-256 |
| --- | --- |
| 设计文档 | `60472580497909c63d627d88a3f9d20d42a3e9c94915151cd430b6047c7b86b1` |
| 正式成品目录（仓库规定算法） | `d23453f2d91ffb3e4fd65cf29fca59736affac53a5908678541f93930e63e26d` |
| ZIP原始字节 | `aaf6e5b06661afb53be3e93e39c54576e879d854ff01dddd23925388d255e04d` |

## 保留的验收限制

20项验收中18项在机械或隔离模拟范围PASS、0项剩余FAIL、2项UNVERIFIED（第2项真实自主暂停、第19项真实Goal/重触发/中断恢复）。真实双AI往返、长期恢复、其他Harness与完整Mermaid渲染亦未实测。完整输入、命令、断言及范围见 `report.md`；这些限制随正式版本保留，不声称全部验收通过。

发布前的 `staged-*`、`production-preserved.json`、`production-verify.txt`、`version-audit.json` 为历史证据；主仓库当前结果以 `release-*` 和正式manifest为准。

## Git与用户已有文件

用户授权在交付后提交并推送现有 `origin/main`；首次同步前fetch确认本地与远端基线均为 `f306bf51537d436647ef7b25e0556ff350777708`。不创建Tag，不强制推送，不改写历史。提交和同步实际结果记录在 `remote-delivery.json`。

用户原有 `install/ruan-project-reader (2).zip` 在构建时保护并原位恢复，SHA-256为 `5e26ef295c9887de641366f70444cbc215fbba780d45316db9da8b4134eb909d`，不纳入本次提交。标准安装包按本次授权重新生成。历史设计/报告、原始修复文档、旧测试夹具、构建脚本和102个既有忽略工作文件均保持原字节。
