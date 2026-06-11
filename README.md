# Email Agent MCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

AI 邮件处理助手，作为 Codex/Claude Code 的 MCP 插件使用。读取收件箱、生成每日总结、起草回复。支持 QQ邮箱 / 163 / Gmail / Outlook / 自定义 IMAP。

## 快速开始

在 Codex 里说 "帮我设置邮箱"。Codex 会自动安装依赖，然后问你几个问题：

- 你用什么邮箱？
- 邮箱地址？授权码？
- 回复偏好？

回答完就配好了，重启 Codex，说 "帮我看看邮件" 即可使用。

## 功能

- **收件箱阅读** — 读取未读邮件（不会标记为已读）
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
| `draft_reply(index, instruction)` | 生成回复草稿 |
| `send_email(to, subject, body)` | 发送邮件 |
| `save_draft(to, subject, body)` | 保存草稿 |
| `list_folders()` | 列出文件夹 |
| `status()` | 查看配置 |

## 项目结构

```
├── SKILL.md                  Codex 技能入口
├── .mcp.json                 Claude Code MCP 配置
├── .codex-plugin/            插件清单
├── scripts/
│   ├── mcp_server.py         MCP 服务器（7个工具）
│   ├── setup.py              备用：终端初始化向导
│   ├── tools.py              IMAP/SMTP 操作
│   ├── summarizer.py         每日总结引擎
│   ├── agent.py              回复生成
│   ├── config.py             配置管理
│   ├── diagnose.py           连接诊断
│   └── mock_emails.py        测试数据
├── references/
│   ├── api_setup.md          授权码配置指南
│   └── email_protocols.md    IMAP/SMTP 参考
└── .env.example              配置模板
```

## 常见问题

**Q: 授权码从哪里获取？**
登录网页邮箱 → 设置 → POP3/IMAP/SMTP → 开启服务 → 生成授权码。详见 `references/api_setup.md`。

**Q: 邮件数据会上传吗？**
不会。所有数据通过本地 MCP 服务器处理，只在你的电脑和邮箱之间传输。

## License

MIT
