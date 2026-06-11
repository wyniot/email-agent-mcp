---
name: email-agent
description: "Automated email processing - read emails, summarize today's inbox, draft replies, and send emails via QQ/163/Gmail/Outlook. Uses MCP tools: mcp__email_agent__read_emails, mcp__email_agent__get_summary, mcp__email_agent__draft_reply, mcp__email_agent__send_email, mcp__email_agent__save_draft, mcp__email_agent__list_folders, mcp__email_agent__status."
---

# Email Agent

This skill lets you process emails through MCP tools. Read inbox, generate summaries, draft replies, send emails.

## Tools

Call `mcp__email_agent__read_emails`, `mcp__email_agent__get_summary`, `mcp__email_agent__draft_reply(index, instruction)`, `mcp__email_agent__send_email(to, subject, body)`, `mcp__email_agent__save_draft(to, subject, body)`, `mcp__email_agent__list_folders`, `mcp__email_agent__status`.

## Setup

First-time users run: `python scripts/setup.py`
Then restart Codex. The MCP server auto-connects.

## Supported Providers

QQ Mail, 163 Mail, Gmail, Outlook/Hotmail, Custom IMAP.
