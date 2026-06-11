[English](#english) | [中文](#中文)

---

# Email Agent MCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

AI email assistant as a Codex / Claude Code MCP plugin. Reads inbox, generates daily summaries, drafts replies. Works with QQ Mail, 163, Gmail, Outlook, and custom IMAP.

AI 邮件处理助手，作为 Codex / Claude Code 的 MCP 插件使用。读取收件箱、生成每日总结、起草回复。支持 QQ邮箱 / 163 / Gmail / Outlook / 自定义 IMAP。

---

## Quick Start / 快速开始

**English:** Say "set up my email" to Codex. It installs dependencies and asks you a few questions (provider, email, auth code, preferences). Done.

**中文：** 在 Codex 里说 "帮我设置邮箱"。Codex 自动安装依赖，然后在聊天里问你：用什么邮箱？邮箱地址？授权码？回复偏好？回答完就配好了。重启 Codex 说 "帮我看看邮件" 即可。

---

## Features / 功能

| English | 中文 |
|---------|------|
| Inbox reader (no auto-mark-read) | 收件箱阅读（不标记已读） |
| Daily email summary by urgency | 每日总结（紧急 / 待回复 / 参考） |
| Auto-draft replies with tone & signature | 自动生成回复草稿（语气+签名） |
| Send or save as draft | 发送或保存草稿 |

## Supported Providers / 支持邮箱

| Provider | Requires | 需要 |
|----------|----------|------|
| QQ Mail / QQ邮箱 | Enable IMAP/SMTP + auth code | 开启 IMAP/SMTP + 授权码 |
| 163 Mail / 163邮箱 | Enable IMAP/SMTP + auth code | 开启 IMAP/SMTP + 授权码 |
| Gmail | 2FA + app password | 两步验证 + 应用专用密码 |
| Outlook | Password or app password | 邮箱密码或应用密码 |
| Custom / 自定义 | Any IMAP/SMTP server | 任意 IMAP/SMTP 服务器 |

## MCP Tools / 工具

| Tool | Description | 说明 |
|------|-------------|------|
| `read_emails(limit)` | Read inbox | 读取收件箱 |
| `get_summary(max)` | Daily summary | 每日总结 |
| `draft_reply(idx, text)` | Draft reply | 生成回复草稿 |
| `send_email(to, sub, body)` | Send email | 发送邮件 |
| `save_draft(to, sub, body)` | Save draft | 保存草稿 |
| `list_folders()` | List folders | 列出文件夹 |
| `status()` | Show config | 查看配置 |

## Project Structure / 项目结构

```
├── SKILL.md                  Codex skill entry / 技能入口
├── .mcp.json                 Claude Code MCP config / 配置
├── .codex-plugin/            Plugin manifest / 插件清单
├── scripts/
│   ├── mcp_server.py         MCP server (7 tools)
│   ├── tools.py              IMAP/SMTP operations
│   ├── summarizer.py         Daily summary engine
│   ├── agent.py              Reply drafting
│   ├── config.py             Config management
│   └── diagnose.py           Connection diagnostics
└── references/
    ├── api_setup.md          Auth code guide / 授权码指南
    └── email_protocols.md    IMAP/SMTP reference / 协议参考
```

## FAQ / 常见问题

**Q: Where do I get an auth code? / 授权码从哪获取？**
Log into webmail > Settings > POP3/IMAP/SMTP > Enable > Generate.
登录网页邮箱 → 设置 → POP3/IMAP/SMTP → 开启服务 → 生成授权码。

**Q: Is my email data uploaded? / 邮件数据会上传吗？**
No. All data stays local via the MCP server running on your machine.
不会。所有数据通过本地 MCP 服务器处理。

**Q: Multiple accounts? / 支持多账号吗？**
Current version supports one account. Rerun setup to switch.
当前版本支持一个邮箱。重新运行 setup 可切换。

## License

MIT
