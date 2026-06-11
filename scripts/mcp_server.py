"""mcp_server.py - Email Agent MCP Server

通过 MCP 协议将邮件处理工具暴露给 AI 客户端。
支持 stdio 传输（本地运行）。

运行: python scripts/mcp_server.py
客户端通过 stdin/stdout JSON-RPC 通信。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from mcp.server import FastMCP
from config import Config

# 默认使用模拟模式测试，真实模式留给用户本地运行
# Respect .env MOCK_MODE by default; EMAIL_MCP_MOCK=true can override for testing
if os.environ.get("EMAIL_MCP_MOCK", "") == "true":
    Config.MOCK_MODE = True

mcp = FastMCP("email-agent")


@mcp.tool()
def read_emails(limit: int = 10) -> str:
    """读取收件箱未读邮件。返回邮件列表（含索引序号）。"""
    from tools import read_emails as _read, format_email_list as _fmt, get_inbox_stats
    emails = _read("INBOX", limit)
    if not emails:
        return "收件箱暂无未读邮件。"
    stats = get_inbox_stats(emails)
    result = _fmt(emails, "收件箱")
    result += "\n\n统计: 共%d封 | 紧急%d | 待回复%d | 参考%d" % (
        len(emails), len(stats["urgent"]), len(stats["reply"]), len(stats["info"]))
    return result


@mcp.tool()
def get_summary(max_emails: int = 20) -> str:
    """生成今日邮件总结，按紧急/待回复/参考分类。"""
    from summarizer import EmailSummarizer
    from config import UserPreferences
    return EmailSummarizer(UserPreferences.load()).summarize_today(max_emails)


@mcp.tool()
def draft_reply(index: int, instruction: str = "") -> str:
    """为指定邮件生成回复草稿。

    Args:
        index: 邮件序号（1开始，对应 read_emails 返回的序号）
        instruction: 回复要点说明，如"告诉他项目已完成80%"
    """
    from tools import read_emails as _read
    from agent import _draft_reply
    from config import UserPreferences
    emails = _read("INBOX", limit=30)
    if not emails:
        return "收件箱暂无邮件。"
    if index < 1 or index > len(emails):
        return "无效序号，请输入 1-%d 之间的数字。" % len(emails)
    target = emails[index - 1]
    tone = UserPreferences.get_reply_tone()
    reply = _draft_reply(target, instruction, tone)
    return ("回复邮件: %s\n发件人: %s\n\n%s" % (
        target["subject"], target["from"]), reply)


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """发送邮件。
    
    Args:
        to: 收件人邮箱
        subject: 邮件主题
        body: 邮件正文
    """
    from tools import send_email as _send
    return _send(to, subject, body)


@mcp.tool()
def save_draft(to: str, subject: str, body: str) -> str:
    """保存邮件草稿。
    
    Args:
        to: 收件人邮箱
        subject: 邮件主题
        body: 邮件正文
    """
    from tools import save_draft as _sd
    return _sd(to, subject, body)


@mcp.tool()
def list_folders() -> str:
    """列出邮箱中的所有文件夹。"""
    from tools import list_folders as _lf
    folders = _lf()
    return "可用文件夹: " + ", ".join(folders)


@mcp.tool()
def status() -> str:
    """查看当前邮件代理配置状态。"""
    from config import Config as C, UserPreferences
    UserPreferences.load()
    lines = [
        "Email Agent MCP Server",
        "=" * 40,
        "邮箱: %s" % C.EMAIL_ACCOUNT,
        "IMAP: %s" % C.EMAIL_IMAP_SERVER,
        "SMTP: %s" % C.EMAIL_SMTP_SERVER,
        "模式: %s" % ("模拟(测试)" if C.MOCK_MODE else "真实"),
        "AI: %s" % C.ai_label(),
        "语气: %s" % UserPreferences.get_reply_tone(),
        "签名: %s" % (UserPreferences.get_signature() or "(无)"),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print("Email Agent MCP Server starting...", file=sys.stderr)
    print("Mode: %s" % ("Mock (testing)" if Config.MOCK_MODE else "Real"), file=sys.stderr)
    mcp.run()
