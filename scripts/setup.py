"""setup.py - Email Agent 初始化配置向导

首次运行时引导用户完成：
1. 配置邮箱（服务商 / IMAP / SMTP / 账号密码）
2. 设置回复偏好（语气 / 自动发送 / 签名）
3. 设置每日邮件总结偏好
4. 保存配置到 user_preferences.json

注意：AI API Key 不需要在这里配置。
需要 AI 增强时，直接在 .env 中添加即可。
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PREFS_FILE = ROOT_DIR / "user_preferences.json"

EMAIL_PROVIDERS = {
    "1": {"name": "Gmail", "imap": "imap.gmail.com", "smtp": "smtp.gmail.com",
          "note": "需开启两步验证并使用「应用专用密码」"},
    "2": {"name": "QQ邮箱", "imap": "imap.qq.com", "smtp": "smtp.qq.com",
          "note": "需开启 IMAP/SMTP 服务并使用「授权码」"},
    "3": {"name": "163邮箱", "imap": "imap.163.com", "smtp": "smtp.163.com",
          "note": "需开启 IMAP/SMTP 服务并使用「授权码」"},
    "4": {"name": "Outlook/Hotmail", "imap": "outlook.office365.com", "smtp": "smtp.office365.com",
          "note": "使用微软邮箱密码或应用密码"},
    "5": {"name": "自定义", "imap": "", "smtp": "",
          "note": "手动输入 IMAP 和 SMTP 服务器地址"},
}

DEFAULT_PREFS = {
    "version": "1.0",
    "setup_complete": False,
    "email": {"provider": "", "imap_server": "", "smtp_server": "", "account": "", "inbox_folder": "INBOX"},
    "preferences": {
        "reply_tone": "正式",
        "auto_send": False,
        "daily_summary": True,
        "summary_at_startup": True,
        "max_summary_emails": 20,
        "watch_senders": [],
        "blacklist_senders": [],
        "signature": "",
    },
}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def load_preferences() -> dict:
    if PREFS_FILE.exists():
        try:
            return json.loads(PREFS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
    return dict(DEFAULT_PREFS)


def save_preferences(prefs: dict) -> None:
    prefs["setup_complete"] = True
    PREFS_FILE.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  \u2705 配置已保存")


def ask(prompt: str, default: str = "") -> str:
    if default:
        val = input(f"  {prompt} [默认: {default}]: ").strip()
        return val if val else default
    return input(f"  {prompt}: ").strip()


def _write_env(key: str, value: str) -> None:
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                found = True
                break
        if not found:
            lines.append(f"{key}={value}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        env_path.write_text(f"{key}={value}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 配置步骤
# ---------------------------------------------------------------------------

def step_email(prefs: dict) -> dict:
    print("\n" + "=" * 60)
    print("  第一步：配置邮箱")
    print("=" * 60)
    print("  请选择邮箱服务商：")
    for k, v in EMAIL_PROVIDERS.items():
        print(f"    {k}. {v['name']}")

    while True:
        choice = input("  请输入编号 [默认: 2 QQ邮箱]: ").strip() or "2"
        if choice in EMAIL_PROVIDERS:
            break
        print("  \u26A0️  无效选择。")

    info = EMAIL_PROVIDERS[choice]
    prefs["email"]["provider"] = info["name"]
    print(f"  📝 提示: {info['note']}")

    acct = ask("请输入邮箱地址")
    if acct:
        prefs["email"]["account"] = acct
        _write_env("EMAIL_ACCOUNT", acct)

    imap = ask("IMAP 服务器", info["imap"]) if choice != "5" else ask("请输入 IMAP 服务器")
    prefs["email"]["imap_server"] = imap
    _write_env("EMAIL_IMAP_SERVER", imap)

    smtp = ask("SMTP 服务器", info["smtp"]) if choice != "5" else ask("请输入 SMTP 服务器")
    prefs["email"]["smtp_server"] = smtp
    _write_env("EMAIL_SMTP_SERVER", smtp)

    pwd = input("  请输入邮箱密码/授权码: ").strip()
    if pwd:
        _write_env("EMAIL_PASSWORD", pwd)

    prefs["email"]["inbox_folder"] = ask("收件箱文件夹名", "INBOX")
    _write_env("EMAIL_INBOX_FOLDER", prefs["email"]["inbox_folder"])
    print("  \u2705 邮箱配置完成")
    return prefs


def step_preferences(prefs: dict) -> dict:
    print("\n" + "=" * 60)
    print("  第二步：回复偏好设置")
    print("=" * 60)

    print("\n  回复语气风格：")
    print("    1. 正式（标准的商务邮件语气）")
    print("    2. 友好（亲切但不失专业）")
    print("    3. 简洁（直达重点，不多废话）")
    tc = input("  请选择 [默认: 1]: ").strip() or "1"
    prefs["preferences"]["reply_tone"] = {"1": "正式", "2": "友好", "3": "简洁"}.get(tc, "正式")

    auto = input("  是否自动发送邮件？（y/n, 默认 n=只保存草稿）: ").strip().lower()
    prefs["preferences"]["auto_send"] = auto in ("y", "yes", "是")

    summary = input("  是否启用「每日邮件总结」？（y/n, 默认 y）: ").strip().lower()
    prefs["preferences"]["daily_summary"] = summary not in ("n", "no", "否")

    watchers = input("  重点关注发件人（逗号分隔，可跳过）: ").strip()
    if watchers:
        prefs["preferences"]["watch_senders"] = [s.strip() for s in watchers.split(",")]

    bl = input("  忽略发件人（逗号分隔，可跳过）: ").strip()
    if bl:
        prefs["preferences"]["blacklist_senders"] = [s.strip() for s in bl.split(",")]

    sig = input("  邮件签名（可跳过）: ").strip()
    if sig:
        prefs["preferences"]["signature"] = sig

    print("  \u2705 偏好设置完成")
    return prefs


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def run_setup() -> dict:
    print("\n" + "█" * 60)
    print("  🚀 欢迎使用 Email Agent")
    print("  首次使用需要完成以下 2 步配置：")
    print("    1. 配置邮箱（支持 Gmail / QQ / 163 / Outlook 等）")
    print("    2. 设置回复偏好和每日总结选项")
    print()
    print("  💡 AI 功能说明：")
    print("    本工具默认使用规则引擎处理邮件，无需任何 API Key。")
    print("    如需 AI 增强（更智能的邮件分析和回复），可在配置完成后")
    print("    在 .env 文件中添加 OPENAI_API_KEY 或 GEMINI_API_KEY。")
    print("█" * 60)

    prefs = load_preferences()
    prefs = step_email(prefs)
    prefs = step_preferences(prefs)
    save_preferences(prefs)

    print("\n" + "=" * 60)
    print("  \u2705 初始化完成！现在可以开始使用了。")
    print("=" * 60)
    print("  常用指令：")
    print("    summary        查看今日邮件总结")
    print("    read           读取收件箱邮件")
    print("    reply <ID>     回复指定邮件")
    print("    help           查看所有指令")
    print()
    print("  💡 AI 增强（可选）：在 .env 中添加 API Key 即可")
    print()

    return prefs


def is_first_run() -> bool:
    prefs = load_preferences()
    return not prefs.get("setup_complete", False)
