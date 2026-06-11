"""diagnose.py - Email Agent 连接诊断工具

在你自己的电脑上运行此脚本，检查：
1. IMAP 连接是否正常
2. SMTP 连接是否正常
3. 配置是否正确

用法: python scripts/diagnose.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config import Config, UserPreferences
UserPreferences.load()


def check(key, value, ok=True):
    tag = "OK" if ok else "!!"
    print("  [%s] %s = %s" % (tag, key, value))
    return ok


def main():
    print()
    print("=" * 55)
    print("  Email Agent - 连接诊断")
    print("=" * 55)

    # 1. 配置文件检查
    print("\n--- 1. 配置文件 ---")
    env_ok = os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
    prefs_ok = os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                            "user_preferences.json"))
    check("环境文件 (.env)", "存在" if env_ok else "缺失", env_ok)
    check("用户配置 (user_preferences.json)", "存在" if prefs_ok else "缺失", prefs_ok)
    print()

    # 2. 邮箱配置
    print("--- 2. 邮箱配置 ---")
    check("服务商", UserPreferences.get("email.provider", "未配置"),
          bool(UserPreferences.get("email.account")))
    check("邮箱地址", Config.EMAIL_ACCOUNT or "(未配置)",
          bool(Config.EMAIL_ACCOUNT))
    check("IMAP 服务器", Config.EMAIL_IMAP_SERVER,
          bool(Config.EMAIL_IMAP_SERVER))
    check("SMTP 服务器", Config.EMAIL_SMTP_SERVER,
          bool(Config.EMAIL_SMTP_SERVER))
    has_pwd = bool(Config.EMAIL_PASSWORD)
    check("密码/授权码", "已配置" if has_pwd else "缺失", has_pwd)
    print()

    # 3. 连接测试
    print("--- 3. 连接测试 ---")
    if not Config.EMAIL_ACCOUNT or not Config.EMAIL_PASSWORD:
        print("  跳过: 邮箱账号或密码未配置")
    else:
        try:
            import imaplib
            print("  \u2192 IMAP: 正在连接 %s ..." % Config.EMAIL_IMAP_SERVER)
            conn = imaplib.IMAP4_SSL(Config.EMAIL_IMAP_SERVER, timeout=10)
            conn.login(Config.EMAIL_ACCOUNT, Config.EMAIL_PASSWORD)
            conn.select("INBOX")
            _s, ids = conn.search(None, "ALL")
            count = len((ids[0] or b"").split()) if ids[0] else 0
            conn.logout()
            check("IMAP", "连接成功（共 %d 封邮件）" % count, True)
        except Exception as e:
            check("IMAP", "连接失败: %s" % e, False)

        try:
            import smtplib
            print("  \u2192 SMTP: 正在连接 %s ..." % Config.EMAIL_SMTP_SERVER)
            with smtplib.SMTP_SSL(Config.EMAIL_SMTP_SERVER, timeout=10) as s:
                s.login(Config.EMAIL_ACCOUNT, Config.EMAIL_PASSWORD)
            check("SMTP", "连接成功", True)
        except Exception as e:
            check("SMTP", "连接失败: %s" % e, False)

    print()

    # 4. AI 配置
    print("--- 4. AI 增强（可选）---")
    if Config.ai_available():
        check("状态", "已启用: %s" % Config.ai_label(), True)
    else:
        print("  [..] 未配置（使用规则引擎，所有功能正常）")
    print()

    # 5. 测试模式
    print("--- 5. 模拟模式 ---")
    check("状态", "启用中（不会接触真实邮箱）" if Config.MOCK_MODE else "关闭（连接真实邮箱）",
          not Config.MOCK_MODE or True)

    print()
    print("=" * 55)
    if Config.MOCK_MODE:
        print("  \u26A0  当前是模拟模式，不会连接真实邮箱")
        print("  在 .env 中设置 MOCK_MODE=false 或")
        print("  运行 python scripts/main.py --real")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
