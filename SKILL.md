---
name: email-agent
description: "Email processing skill - read inbox, generate daily summaries, and draft replies for QQ Mail, 163, Gmail, Outlook, and any IMAP/SMTP email. First-time setup guides the user through email provider selection, credentials, and reply preferences."
---

# Email Agent

This skill lets Codex read your inbox, generate daily email summaries, draft replies, and send emails — through MCP tools that run locally on your machine.

## First-Time Setup (3 steps)

When a new user first mentions email, guide them:

**Step 1**: Tell them to run the setup wizard in their terminal:

```bash
cd <project-path>
pip install python-dotenv
python scripts/setup.py
```

**Step 2**: The wizard asks:
- "Which email provider?" → QQ / 163 / Gmail / Outlook / Custom
- "Email address?" → user@qq.com
- "Authorization code?" → (app-specific password)
- "Reply tone?" → Formal / Friendly / Concise
- "Auto-send or save draft?"
- "Signature?"

The wizard auto-fills IMAP/SMTP server addresses for known providers.

**Step 3**: After setup completes, tell them to restart Codex. The Email Agent MCP server will auto-connect.

## MCP Tools

| Tool | Description |
|------|-------------|
| `mcp__email_agent__read_emails(limit)` | Read inbox emails (not marks as read) |
| `mcp__email_agent__get_summary(max)` | Generate daily email summary by urgency |
| `mcp__email_agent__draft_reply(index, instruction)` | Draft reply by list position |
| `mcp__email_agent__send_email(to, subject, body)` | Send an email |
| `mcp__email_agent__save_draft(to, subject, body)` | Save as draft |
| `mcp__email_agent__list_folders()` | List email folders |
| `mcp__email_agent__status()` | Show current config |

## Daily Use

Once set up, the user just talks naturally:

- "帮我看看邮件" → `read_emails`
- "总结今天的邮件" → `get_summary`
- "回复第3封，收到" → `draft_reply(3, "收到")`
- "发邮件给xxx" → `send_email`
- "保存草稿" → `save_draft`

## Supported Providers

All providers that support IMAP/SMTP with authorization codes (app passwords):

QQ Mail, 163 Mail, Gmail, Outlook/Hotmail, and any custom IMAP server.

The setup wizard auto-fills server addresses. Authorization code setup instructions are in `references/api_setup.md`.

## Files

- `scripts/setup.py` — Interactive setup wizard (run once)
- `scripts/mcp_server.py` — MCP server (launched by Codex)
- `scripts/tools.py` — IMAP/SMTP email tools
- `scripts/summarizer.py` — Email classification & summary
- `scripts/agent.py` — AI reply drafting (optional)
- `scripts/mock_emails.py` — Test data for development
- `references/api_setup.md` — Authorization code guides per provider
