# Email Agent MCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

AI 邮件处理助手 — 作为 Codex/Claude Code 的 MCP 插件使用，读取收件箱、生成每日总结、起草回复。支持 QQ邮箱 / 163 / Gmail / Outlook 等所有 IMAP 邮箱。

## 快速开始

### 1. 安装依赖

```bash
pip install python-dotenv
```

### 2. 运行初始化向导

```bash
python scripts/setup.py
```

向导会引导你完成：选择邮箱服务商 → 输入邮箱地址和授权码 → 设置回复偏好 → 配置每日总结。

### 3. 重启 Codex，开始使用

在聊天里直接说：

> "帮我看看邮件"
> "总结今天的邮件"
> "回复第 3 封，已收到"

Codex 会自动调用 MCP 工具读取你的收件箱。

## 功能

- **收件箱阅读** — 读取未读邮件（不会标记为已读）
- **每日总结** — 按⚡紧急 / 📌待回复 / 📖参考自动分类
- **回复草稿** — 用设定好的语气和签名自动生成
- **发送/草稿** — 支持直接发送或保存草稿
- **多邮箱支持** — QQ / 163 / Gmail / Outlook / 自定义 IMAP

## 支持邮箱

| 邮箱 | 需要 |
|------|------|
| QQ 邮箱 | 开启 IMAP/SMTP + 授权码 |
| 163 邮箱 | 开启 IMAP/SMTP + 授权码 |
| Gmail | 两步验证 + 应用专用密码 |
| Outlook / Hotmail | 邮箱密码或应用密码 |
| 自定义 | 任意 IMAP/SMTP 服务器 |

## MCP 工具

| 工具 | 说明 |
|------|------|
| `read_emails(limit)` | 读取收件箱 |
| `get_summary(max)` | 每日邮件总结 |
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
│   ├── setup.py              ⭐ 初始化向导
│   ├── mcp_server.py         ⭐ MCP 服务器
│   ├── tools.py              IMAP/SMTP 操作
│   ├── summarizer.py         每日总结引擎
│   ├── agent.py              回复生成
│   ├── config.py             配置管理
│   ├── main.py               CLI 入口
│   ├── diagnose.py           连接诊断
│   ├── mock_emails.py        测试数据
│   └── memory.py             记忆模块
├── references/
│   ├── api_setup.md          授权码配置指南
│   └── email_protocols.md    IMAP/SMTP 参考
└── .env.example              配置模板
```

## 常见问题

**Q: 授权码从哪里获取？**
登录网页邮箱 → 设置 → POP3/IMAP/SMTP → 开启服务 → 生成授权码。详见 `references/api_setup.md`。

**Q: 邮件会被上传到云端吗？**
不会。所有数据通过本地 MCP 服务器处理，只在你电脑和邮箱服务器之间传输。

**Q: 支持多个邮箱吗？**
当前版本支持一个邮箱。如需切换，重新运行 `python scripts/setup.py`。

## License

MIT
