# Email Agent MCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

<details open>
<summary><b>&#x1f1e8;&#x1f1f3; 中文</b></summary>

AI 邮件处理助手，作为 Codex / Claude Code 的 MCP 插件使用。读取收件箱、生成每日总结、起草回复。支持 QQ邮箱 / 163 / Gmail / Outlook / 自定义 IMAP。

## 快速开始

在 Codex 里说 **"帮我设置邮箱"**。Codex 自动安装依赖，然后在聊天里问你：

- 用什么邮箱？
- 邮箱地址？
- 授权码？
- 回复偏好？

回答完就配好了。重启 Codex，说 "帮我看看邮件" 即可使用。

## 功能

- **收件箱阅读** — 读取未读邮件（不标记已读）
- **每日总结** — 按⚡紧急 / 📌待回复 / 📖参考自动分类
- **回复草稿** — 用设定好的语气和签名自动生成
- **发送/草稿** — 支持直接发送或保存草稿

## 支持邮箱

| 邮箱 | 需要 |
|------|------|
| QQ邮箱 | 开启 IMAP/SMTP + 授权码 |
| 163邮箱 | 开启 IMAP/SMTP + 授权码 |
| Gmail | 两步验证 + 应用专用密码 |
| Outlook | 邮箱密码或应用密码 |
| 自定义 | 任意 IMAP/SMTP 服务器 |

## MCP 工具

| 工具 | 说明 |
|------|------|
| `read_emails(limit)` | 读取收件箱 |
| `get_summary(max)` | 每日总结 |
| `draft_reply(idx, text)` | 生成回复草稿 |
| `send_email(to, sub, body)` | 发送邮件 |
| `save_draft(to, sub, body)` | 保存草稿 |
| `list_folders()` | 列出文件夹 |
| `status()` | 查看配置 |

## 项目结构

```
├── SKILL.md                  Codex 技能入口
├── .mcp.json                 Claude Code MCP 配置
├── .codex-plugin/            插件清单
├── scripts/
│   ├── mcp_server.py         MCP 服务器（7 个工具）
│   ├── tools.py              IMAP/SMTP 操作
│   ├── summarizer.py         每日总结引擎
│   ├── agent.py              回复生成
│   ├── config.py             配置管理
│   └── diagnose.py           连接诊断
└── references/
    ├── api_setup.md          授权码配置指南
    └── email_protocols.md    IMAP/SMTP 参考
```

## 常见问题

**Q: 授权码从哪里获取？**
登录网页邮箱 → 设置 → POP3/IMAP/SMTP → 开启服务 → 生成授权码。

**Q: 邮件数据会上传吗？**
不会。所有数据通过本地 MCP 服务器处理，只在你的电脑和邮箱之间传输。

**Q: 支持多账号吗？**
当前版本支持一个邮箱。重新运行 setup 可切换。

</details>

<details>
<summary><b>&#x1f1fa;&#x1f1f8; English</b></summary>

AI email assistant as a Codex / Claude Code MCP plugin. Reads inbox, generates daily summaries, drafts replies. Works with QQ Mail, 163, Gmail, Outlook, and custom IMAP.

## Quick Start

Say **"set up my email"** to Codex. It installs dependencies and asks you a few questions (provider, email, auth code, preferences). Done. Restart Codex and say "check my emails".

## Features

- **Inbox reader** — read unread emails (no auto-mark-read)
- **Daily summary** — categorized by urgency / needs-reply / FYI
- **Reply drafting** — auto-drafted with your tone and signature
- **Send / save draft** — choose to send directly or save as draft

## Supported Providers

| Provider | Requires |
|----------|----------|
| QQ Mail | Enable IMAP/SMTP + auth code |
| 163 Mail | Enable IMAP/SMTP + auth code |
| Gmail | 2FA + app password |
| Outlook | Password or app password |
| Custom | Any IMAP/SMTP server |

## MCP Tools

| Tool | Description |
|------|-------------|
| `read_emails(limit)` | Read inbox |
| `get_summary(max)` | Daily summary |
| `draft_reply(idx, text)` | Draft reply |
| `send_email(to, sub, body)` | Send email |
| `save_draft(to, sub, body)` | Save draft |
| `list_folders()` | List folders |
| `status()` | Show config |

## Project Structure

```
├── SKILL.md                  Codex skill entry
├── .mcp.json                 Claude Code MCP config
├── .codex-plugin/            Plugin manifest
├── scripts/
│   ├── mcp_server.py         MCP server (7 tools)
│   ├── tools.py              IMAP/SMTP operations
│   ├── summarizer.py         Daily summary engine
│   ├── agent.py              Reply drafting
│   ├── config.py             Config management
│   └── diagnose.py           Connection diagnostics
└── references/
    ├── api_setup.md          Auth code setup guide
    └── email_protocols.md    IMAP/SMTP reference
```

## FAQ

**Q: Where do I get an auth code?**
Log into webmail > Settings > POP3/IMAP/SMTP > Enable > Generate.

**Q: Is my email data uploaded?**
No. All data stays local via the MCP server running on your machine.

**Q: Multiple accounts?**
Current version supports one account. Rerun setup to switch.

</details>

## License

MIT
