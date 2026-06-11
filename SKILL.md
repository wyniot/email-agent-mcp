---
name: email-agent
description: "Email processing skill - read inbox, generate daily summaries, and draft replies for QQ Mail, 163, Gmail, Outlook, and any IMAP/SMTP email. First-time setup asks the user which email provider they use, their email address, auth code, and reply preferences."
---

# Email Agent

This skill lets Codex read inbox emails, generate daily summaries, draft replies, and send emails through MCP tools running locally.

## First-Time Setup

When a user first asks about email and setup hasn't been done yet (no `user_preferences.json`):

**Step 1** — Install the dependency automatically:

```bash
pip install python-dotenv
```

**Step 2** — Ask the user these questions (one at a time, in this order):

1. "你用什么邮箱？"
   - Options: QQ邮箱 / 163邮箱 / Gmail / Outlook / 自定义
2. "请输入邮箱地址"  
3. "请输入授权码"（提示: 在网页邮箱设置里开启 IMAP/SMTP 后生成）
4. "回复语气偏好？" — Options: 正式 / 友好 / 简洁
5. "自动发送还是保存草稿？" — Options: 自动发送 / 保存草稿
6. "邮件签名？（可跳过）"
7. "启用每日邮件总结？" — Options: 是 / 否

**Step 3** — After collecting all answers, write the config. Use the IMAP/SMTP defaults:

- QQ邮箱: imap.qq.com / smtp.qq.com
- 163邮箱: imap.163.com / smtp.163.com  
- Gmail: imap.gmail.com / smtp.gmail.com
- Outlook: outlook.office365.com / smtp.office365.com
- 自定义: ask the user for server addresses

Write to `.env` and `user_preferences.json` using the helper:

```python
import json
# Write .env
with open('.env', 'w', encoding='utf-8') as f:
    f.write(f"""EMAIL_IMAP_SERVER={imap_server}
EMAIL_SMTP_SERVER={smtp_server}
EMAIL_ACCOUNT={email}
EMAIL_PASSWORD={auth_code}
EMAIL_INBOX_FOLDER=INBOX
MOCK_MODE=false
""")
# Write user_preferences.json
prefs = {
    "version": "1.0", "setup_complete": True,
    "email": {"provider": provider_name, "imap_server": imap_server, "smtp_server": smtp_server, "account": email, "inbox_folder": "INBOX"},
    "preferences": {"reply_tone": tone, "auto_send": auto_send, "daily_summary": daily_summary, "summary_at_startup": True, "max_summary_emails": 20, "watch_senders": [], "blacklist_senders": [], "signature": signature}
}
json.dump(prefs, open('user_preferences.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
```

**Step 4** — Tell the user: "配置完成！重启 Codex 后对我说 '帮我看邮件' 即可。"

## MCP Tools (available after restart)

| Tool | Description |
|------|-------------|
| `mcp__email_agent__read_emails(limit)` | Read inbox (does not mark as read) |
| `mcp__email_agent__get_summary(max)` | Daily summary by urgency |
| `mcp__email_agent__draft_reply(index, instruction)` | Draft reply by position |
| `mcp__email_agent__send_email(to, subject, body)` | Send email |
| `mcp__email_agent__save_draft(to, subject, body)` | Save draft |
| `mcp__email_agent__list_folders()` | List folders |
| `mcp__email_agent__status()` | Show config |

## Daily Use

Once set up, the user just talks naturally:

- "帮我看看邮件" → `read_emails`
- "总结今天的邮件" → `get_summary`
- "回复第3封，收到" → `draft_reply(3, "收到")`
- "发邮件给xxx@qq.com，主题是..." → `send_email`

## Supported Providers

QQ Mail / 163 Mail / Gmail / Outlook / Hotmail / Custom IMAP.

Setup instructions for authorization codes are in `references/api_setup.md`.

## Files

- `scripts/mcp_server.py` — MCP server (launched by Codex after restart)
- `scripts/tools.py` — IMAP/SMTP email operations
- `scripts/summarizer.py` — Email classification & summary
- `scripts/agent.py` — AI reply drafting
- `scripts/config.py` — Configuration loading
- `references/api_setup.md` — Per-provider auth code guides
