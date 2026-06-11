"""tools.py - Email tools for the Email Agent.

Provides core tools the agent can call:
1. read_emails(folder, limit) - Read from IMAP or mock data
2. send_email(to, subject, body) - Send via SMTP
3. save_draft(to, subject, body) - Save as draft via SMTP
4. list_folders() - List available IMAP folders
5. test_connection() - Test IMAP/SMTP connectivity
6. get_inbox_stats(emails) - Categorize emails for overview

All tools handle connection errors gracefully.
"""

import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from typing import Any

from config import Config, UserPreferences


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _decode_mime_header(raw: str) -> str:
    if not raw:
        return ""
    parts = []
    for decoded_bytes, charset in decode_header(raw):
        if isinstance(decoded_bytes, bytes):
            try:
                parts.append(decoded_bytes.decode(charset or "utf-8"))
            except (LookupError, UnicodeDecodeError):
                for enc in ("utf-8", "gbk", "gb2312", "gb18030", "big5"):
                    try:
                        parts.append(decoded_bytes.decode(enc))
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    parts.append(decoded_bytes.decode("latin-1"))
        else:
            parts.append(str(decoded_bytes))
    return "".join(parts)


def _decode_email_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        return payload.decode(charset)
                    except (LookupError, UnicodeDecodeError):
                        return payload.decode("utf-8", errors="replace")
        return ""
    payload = msg.get_payload(decode=True)
    if payload:
        charset = msg.get_content_charset() or "utf-8"
        try:
            return payload.decode(charset)
        except (LookupError, UnicodeDecodeError):
            return payload.decode("utf-8", errors="replace")
    return ""


def _add_signature(body: str) -> str:
    sig = UserPreferences.get_signature()
    if sig and sig not in body:
        return "%s\n\n--\n%s" % (body, sig)
    return body


# ---------------------------------------------------------------------------
# IMAP connection (internal, error-reporting)
# ---------------------------------------------------------------------------

def _connect_imap():
    """Open an IMAP SSL connection. Raises ConnectionError on failure."""
    server = Config.EMAIL_IMAP_SERVER
    account = Config.EMAIL_ACCOUNT
    password = Config.EMAIL_PASSWORD

    if not account or not password:
        raise ConnectionError("邮箱账号或密码未配置（请检查 .env 文件）")

    try:
        conn = imaplib.IMAP4_SSL(server, timeout=15)
        conn.login(account, password)
        return conn
    except imaplib.IMAP4.error as e:
        raise ConnectionError("IMAP 登录失败: %s\n请检查邮箱地址和授权码是否正确。" % e)
    except socket_error as e:
        raise ConnectionError("无法连接到 %s: %s\n请检查网络连接或防火墙设置。" % (server, e))
    except Exception as e:
        raise ConnectionError("连接 IMAP 服务器 %s 失败: %s" % (server, e))


# ---------------------------------------------------------------------------
# Test connection
# ---------------------------------------------------------------------------

def test_connection():
    """测试 IMAP/SMTP 连接是否正常。返回 (ok: bool, message: str)。"""
    print("  [诊断] 正在测试邮件服务器连接...")

    # Test IMAP
    try:
        conn = imaplib.IMAP4_SSL(Config.EMAIL_IMAP_SERVER, timeout=10)
        conn.login(Config.EMAIL_ACCOUNT, Config.EMAIL_PASSWORD)
        conn.select("INBOX")
        _status, msg_ids = conn.search(None, "ALL")
        count = len((msg_ids[0] or b"").split()) if msg_ids[0] else 0
        conn.logout()
        print("  [诊断] IMAP: OK (%d 封邮件)" % count)
    except Exception as e:
        return (False, "IMAP 连接失败: %s" % e)

    # Test SMTP
    try:
        with smtplib.SMTP_SSL(Config.EMAIL_SMTP_SERVER, timeout=10) as server:
            server.login(Config.EMAIL_ACCOUNT, Config.EMAIL_PASSWORD)
        print("  [诊断] SMTP: OK")
    except Exception as e:
        return (False, "SMTP 连接失败: %s" % e)

    return (True, "邮件服务器连接正常！")


try:
    from socket import error as socket_error
except ImportError:
    socket_error = Exception


# ---------------------------------------------------------------------------
# Public tools
# ---------------------------------------------------------------------------

def read_emails(folder="INBOX", limit=10):
    """读取指定文件夹的邮件。

    Mock 模式下使用内置模拟数据；真实模式连接 IMAP 服务器。
    连接失败时返回空列表并打印错误信息。
    """
    if Config.MOCK_MODE:
        print("  [工具] 读取模拟邮件 (folder=%s, limit=%d)" % (folder, limit))
        from mock_emails import load_mock_emails as _load_mock
        return _load_mock(folder, limit)

    print("  [工具] 连接 IMAP %s ..." % Config.EMAIL_IMAP_SERVER)
    try:
        conn = _connect_imap()
    except ConnectionError as e:
        print("  [工具] %s" % e)
        print("  [工具] 请运行 python scripts/diagnose.py 检查配置")
        print("  [工具] 或设置 MOCK_MODE=true 使用模拟数据测试")
        return []

    try:
        result = conn.select(folder)
        if result[0] != "OK":
            print("  [工具] 文件夹 '%s' 无法打开，尝试大写..." % folder)
            result = conn.select(folder.upper())
        if result[0] != "OK":
            print("  [工具] 尝试小写...")
            result = conn.select(folder.lower())
        if result[0] != "OK":
            err_msg = str(result[1])
            print("  [工具] 无法打开收件箱: %s" % err_msg)
            if "Unsafe Login" in err_msg:
                print()
                print("  ========== 163 邮箱安全拦截 ==========")
                print("  163 邮箱认为此次 IMAP 连接存在安全风险，已拦截。")
                print("  请按以下步骤处理：")
                print("  1. 打开浏览器登录 https://mail.163.com")
                print("  2. 进入设置 -> POP3/SMTP/IMAP 确认服务已开启")
                print("  3. 检查是否有安全通知，确认此次登录为本人操作")
                print("  4. 或重新生成一个新的授权码")
                print("  5. 仍有问题请联系 163 客服: kefu@188.com")
                print("  ========================================")
                print()
            else:
                print("  请运行 python scripts/diagnose.py 检查配置")
            return []
        _status, msg_ids = conn.search(None, "UNSEEN")
        ids = (msg_ids[0] or b"").split()
        if not ids:
            return []

        results = []
        for mid in reversed(ids[-limit:]):
            _ok, data = conn.fetch(mid, "(BODY.PEEK[])")
            raw = data[0][1] if data and data[0] else None
            if not raw:
                continue
            msg = email.message_from_bytes(raw)
            results.append({
                "id": mid.decode(),
                "from": _decode_mime_header(msg.get("From", "")),
                "subject": _decode_mime_header(msg.get("Subject", "")),
                "body": _decode_email_body(msg),
                "date": msg.get("Date", ""),
                "urgency": "reply",
            })
        print("  [工具] 读取到 %d 封未读邮件" % len(results))
        return results
    finally:
        conn.logout()


def send_email(to, subject, body):
    """发送邮件。Mock 模式仅打印，自动追加签名。"""
    body = _add_signature(body)

    if Config.MOCK_MODE:
        print("  [工具] [模拟发送] To: %s" % to)
        return "[模拟] 邮件已发送至 %s" % to

    print("  [工具] 通过 SMTP %s 发送 ..." % Config.EMAIL_SMTP_SERVER)
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = Config.EMAIL_ACCOUNT
    msg["To"] = to
    msg["Subject"] = subject

    try:
        with smtplib.SMTP_SSL(Config.EMAIL_SMTP_SERVER, timeout=15) as server:
            server.login(Config.EMAIL_ACCOUNT, Config.EMAIL_PASSWORD)
            server.send_message(msg)
        return "邮件已成功发送至 %s" % to
    except Exception as e:
        return "发送失败: %s" % e


def save_draft(to, subject, body):
    """保存邮件草稿。Mock 模式仅打印，自动追加签名。"""
    body = _add_signature(body)

    if Config.MOCK_MODE:
        print("  [工具] [模拟保存草稿] To: %s" % to)
        return "[模拟] 草稿已保存（收件人: %s）" % to

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = Config.EMAIL_ACCOUNT
    msg["To"] = to
    msg["Subject"] = subject

    try:
        conn = _connect_imap()
        try:
            conn.append("Drafts", None, None, msg.as_bytes())
            return "草稿已保存（收件人: %s）" % to
        finally:
            conn.logout()
    except Exception as e:
        return "保存草稿失败: %s" % e


def list_folders():
    """列出邮箱中的所有文件夹。"""
    if Config.MOCK_MODE:
        return ["INBOX", "Sent", "Drafts", "Spam", "Archive"]

    try:
        conn = _connect_imap()
    except ConnectionError as e:
        print("  [工具] %s" % e)
        return []

    try:
        _status, folders = conn.list()
        names = []
        for raw in folders:
            decoded = raw.decode()
            parts = decoded.split('"')
            if len(parts) >= 3:
                names.append(parts[-2].strip())
            else:
                names.append(decoded.rsplit("/", 1)[-1].strip())
        return names
    finally:
        conn.logout()


# ---------------------------------------------------------------------------
# Inbox stats & formatting
# ---------------------------------------------------------------------------

def get_inbox_stats(emails):
    """对邮件列表进行快速分类统计（无需 AI）。"""
    urgent_kw = ["紧急", "urgent", "故障", "告警", "bug", "问题", "重要", "asap", "deadline", "P0"]
    reply_kw = ["确认", "回复", "请教", "讨论", "审批", "申请", "反馈", "意见", "盼复"]

    result = {"total": len(emails), "urgent": [], "reply": [], "info": []}

    for e in emails:
        subj = e["subject"].lower()
        body = e["body"].lower()[:200]
        urg = e.get("urgency", "")

        if urg == "urgent":
            result["urgent"].append(e)
        elif urg == "reply":
            result["reply"].append(e)
        elif any(k in subj or k in body for k in urgent_kw):
            result["urgent"].append(e)
        elif any(k in subj or k in body for k in reply_kw):
            result["reply"].append(e)
        else:
            result["info"].append(e)

    return result


def format_email_list(emails, title="邮件列表"):
    """将邮件列表格式化为可读字符串。"""
    if not emails:
        return "收件箱: 暂无邮件"

    lines = ["收件箱 (共 %d 封)" % len(emails)]
    for i, e in enumerate(emails, 1):
        tag = {"urgent": "[!]", "reply": "[R]", "info": "[ ]"}.get(e.get("urgency", "info"), "[ ]")
        sender_short = e["from"].split("<")[0].strip()[:18]
        lines.append("  %s [%02d] %s | %s" % (tag, i, e["id"], e["subject"]))
    lines.append("  >>> 输入 reply <ID> <内容> 回复")
    return "\n".join(lines)
