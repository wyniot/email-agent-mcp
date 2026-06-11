"""main.py - Email Agent CLI 入口

功能：
- 首次运行自动启动配置向导
- 启动时根据偏好显示今日邮件总结
- 交互式命令：summary / read / reply / send / draft / list / history
- 无需 API Key，规则引擎默认工作
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config import Config, UserPreferences
from agent import EmailAgent
from tools import read_emails, format_email_list, get_inbox_stats
from setup import run_setup, is_first_run


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Email Agent - AI 邮件处理智能助手")
    p.add_argument("--real", action="store_true", help="连接真实邮箱")
    p.add_argument("--no-summary", action="store_true", help="启动时不显示今日总结")
    p.add_argument("--reset", action="store_true", help="重置配置")
    return p.parse_args()


def startup(args: argparse.Namespace) -> EmailAgent:
    if args.reset:
        prefs_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  "user_preferences.json")
        if os.path.exists(prefs_file):
            os.remove(prefs_file)
            print("  \u2757 配置已重置")

    if args.real:
        Config.MOCK_MODE = False

    if is_first_run():
        run_setup()
    else:
        UserPreferences.load()

    warnings = Config.validate()
    if warnings:
        for w in warnings:
            print(f"  \u26A0\ufe0f  {w}")

    print(f"\n  {'='*50}")
    print(f"  邮箱:     {Config.EMAIL_ACCOUNT or '(模拟邮箱)'}")
    print(f"  AI 模式:  {Config.ai_label()}")
    print(f"  模式:     {'模拟数据' if Config.MOCK_MODE else '真实邮箱'}")
    print(f"  {'='*50}")

    agent = EmailAgent()

    if (not args.no_summary
            and UserPreferences.get_daily_summary_enabled()
            and UserPreferences.get_summary_at_startup()):
        print("\n  \U0001F4CB 今日邮件总结:")
        print()
        print(agent.summarize_today())

    return agent


def print_help():
    print()
    print("  \U0001F4CB 命令:")
    print("  " + "-"*50)
    print("  summary      今日邮件总结")
    print("  read         读取收件箱")
    print("  reply <ID>   回复指定邮件")
    print("  send         撰写并发送")
    print("  draft        撰写并保存草稿")
    print("  list         列出文件夹")
    print("  history      处理历史")
    print("  help         帮助")
    print("  exit         退出")
    print("  " + "-"*50)
    print("  也可以直接输入自然语言指令（需配置 API Key）")
    print()


def interactive_loop(agent: EmailAgent):
    print("\n  输入 help 查看命令，exit 退出。\n")

    while True:
        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  \U0001F44B 再见！")
            break

        if not raw:
            continue

        cmd = raw.lower()

        if cmd in ("exit", "quit", "q"):
            print("  \U0001F44B 再见！")
            break
        if cmd == "help":
            print_help()
            continue
        if cmd == "history":
            print(f"\n{agent.get_memory_summary()}")
            continue
        if cmd == "list":
            from tools import list_folders as lf
            print(f"\n  \U0001F4C1 文件夹: {', '.join(lf())}")
            continue
        if cmd == "summary":
            print("\n  \U0001F4CB 今日邮件总结:")
            print(agent.summarize_today())
            continue
        if cmd == "read":
            emails = read_emails()
            stats = get_inbox_stats(emails)
            print(f"\n{format_email_list(emails, '收件箱')}")
            print(f"  \U0001F4CA 统计: 共{stats['total']}封 | "
                  f"\u26a1紧急{len(stats['urgent'])} | "
                  f"\U0001F4CC待回复{len(stats['reply'])} | "
                  f"\U0001F4D6参考{len(stats['info'])}")
            continue
        if cmd.startswith("reply "):
            parts = cmd[6:].strip().split(" ", 1)
            eid = parts[0]
            text = parts[1] if len(parts) > 1 else ""
            emails = read_emails()
            target = next((e for e in emails if e["id"] == eid), None)
            if not target:
                print(f"\n  \u26A0\ufe0f 未找到邮件 {eid}")
                continue
            result = agent.run(f"reply {eid} {text}")
            print(f"\n{result}")
            continue

        # send/draft 交互式
        if cmd in ("send",):
            to = input("  收件人: ").strip()
            sub = input("  主题: ").strip()
            print("  正文（输入 ;; 结束）:")
            body = "\n".join(iter(lambda: input("  ").strip(), ";;"))
            if to and sub and body:
                from tools import send_email as se
                print(f"\n  {se(to, sub, body)}")
            continue
        if cmd in ("draft",):
            to = input("  收件人: ").strip()
            sub = input("  主题: ").strip()
            print("  正文（输入 ;; 结束）:")
            body = "\n".join(iter(lambda: input("  ").strip(), ";;"))
            if to and sub and body:
                from tools import save_draft as sd
                print(f"\n  {sd(to, sub, body)}")
            continue

        # 自然语言指令
        result = agent.run(raw)
        print(f"\n{result}")


def main():
    args = parse_args()
    agent = startup(args)
    interactive_loop(agent)


if __name__ == "__main__":
    main()
