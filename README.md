# ruan-project-reader

`ruan-project-reader` 这个 Agent Skill 的开发仓库。仓库按「设计、开发、交付」三个目录组织，方便跨设备、跨 AI 会话长期维护。

## 目录

| 路径 | 内容 |
|---|---|
| `design/` | 各版本的设计文档，目标版本以其中最新的已确认（`approved`）版本为准 |
| `src/` | 开发源码（`src/ruan-project-reader/`）、长期测试（`src/tests/`） |
| `install/` | 当前正式发布的、可直接复制安装的 Skill；未发布时为空 |
| `AGENTS.md` | AI 维护约定，规则以它为准 |

## 开始开发

1. 复制 `design/templates/version.md` 到 `design/versions/<版本号>.md`，写下这一版要做什么，经你确认后把 `status` 改为 `approved`。详细规则见 `design/README.md`。
2. 让 AI 助手阅读 `AGENTS.md`，再说「按最新设计版本开始开发」。它会先核对设计、源码和成品的状态再动手。
3. 验收通过后，AI 助手才会从 `src/` 构建 `install/`。

## 安装成品

当前正式版本为 **2.4**，工程版本为 **2.4.0**，对应 [已确认设计](design/versions/2.4.0.md)。成品已从开发源构建并核验，发布详情见 [发布记录](reports/2.4-2026-10-30/release.md) 和 `install/.release.json`。把 `install/ruan-project-reader/` 整个目录复制到你的 AI 工具的 Skills 目录即可，也可解压 [安装包](install/ruan-project-reader.zip) 后复制其中同名目录。

2.4 使用标准 Agent Skills 目录与相对资源路径，运行核心不依赖特定模型、MCP 或联网服务。Codex、Claude Code、DeepSeek Harness 等平台按各自的 Skill 加载方式安装；具体 Harness 需支持本地 Skill，不能仅凭模型名称认定安装位置。检查器需要 Python 3.10+ 标准库。正式转正及整体完成必须由 Python 或可信同算法工具实际计算指纹；没有可信计算能力时可继续调查、保存草稿或待验收，但指纹未验证，用户表示认可也不能转正。工具恢复后须重算并重新确认具体版本。

本版按“本地核验通过 → 待验收 → 用户明确认可当前文件指纹版本 → 独立授权继续”运行，完整稿默认文件回传。各模块先验收，再对整体清单确认。已有知识库默认只读检查；合法三状态/八统计结构返回 UNVERIFIED（退出2），格式迁移须用户明确触发。完整证据及真实平台未验证范围见 [验收报告](reports/2.4-2026-10-30/report.md)。

## 验证与构建

```bash
python3 -m unittest discover -s src/tests -v
python3 src/build_release.py --build
python3 src/build_release.py --verify
```

构建会重跑回归、核验原成品、从开发源暂存完整新成品，并生成规定的发布清单。设计语义验收见 [2.4 验收记录](reports/2.4-2026-10-30/report.md)；[2.2.0 验收记录](src/tests/acceptance-2.2.0.md) 保留作历史依据。测试与平台限制见 [测试说明](src/tests/README.md)。不会自动提交、推送或打 Tag。

## 用 GitHub 同步

这个仓库已准备好直接纳入 Git。关联远程仓库、推送和打 Tag 由你自己决定，AI 助手需要你明确授权才会执行。
