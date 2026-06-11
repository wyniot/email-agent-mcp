"""summarizer.py - 每日邮件总结引擎

默认使用规则引擎（关键词分类 + 模板格式化），无需 API Key。
如果配置了 API Key，自动使用 AI 增强分类和摘要。
"""

from datetime import date
from pathlib import Path
from typing import Any

from config import Config
from tools import read_emails

ROOT_DIR = Path(__file__).resolve().parent.parent
SUMMARY_DIR = ROOT_DIR / "summaries"


class EmailSummarizer:
    """邮件总结器。默认规则引擎，AI 增强可选。"""

    def __init__(self, preferences: dict | None = None):
        self.prefs = preferences or {}

    def summarize_today(self, max_emails: int = 20) -> str:
        """生成今日邮件总结。"""
        print("  [总结] 正在读取邮件...")
        emails = read_emails("INBOX", limit=max_emails)

        if not emails:
            return self._no_emails_report()

        # 过滤黑名单
        blacklist = self.prefs.get("preferences", {}).get("blacklist_senders", [])
        if blacklist:
            emails = [e for e in emails if not any(b in e["from"] for b in blacklist)]

        print(f"  [总结] 读取到 {len(emails)} 封")

        # 如果有 AI 增强，使用 AI 总结
        if Config.ai_available():
            try:
                report = self._ai_summarize(emails)
                self._save_summary(report)
                return report
            except Exception as e:
                print(f"  [总结] AI 总结失败，使用规则引擎: {e}")

        # 规则引擎总结
        report = self._fallback_summary(emails)
        self._save_summary(report)
        return report

    def _fallback_summary(self, emails: list[dict]) -> str:
        """基于关键词分类的规则引擎总结（无需 API Key）。"""
        today_str = date.today().isoformat()
        urgent_kw = ["紧急", "urgent", "故障", "告警", "bug", "问题", "重要", "asap", "P0"]
        reply_kw = ["确认", "回复", "请教", "讨论", "审批", "申请", "反馈", "意见", "盼复"]

        urgent, needs_reply, info = [], [], []

        for e in emails:
            subj = e["subject"].lower()
            body = e["body"].lower()[:200]
            urg = e.get("urgency", "")

            if urg == "urgent" or any(k in subj or k in body for k in urgent_kw):
                urgent.append(e)
            elif urg == "reply" or any(k in subj or k in body for k in reply_kw):
                needs_reply.append(e)
            else:
                info.append(e)

        lines = [
            f"  {'='*50}",
            f"  今日邮件总结 ({today_str})",
            f"  {'='*50}",
        ]

        if urgent:
            lines.append(f"\n  ⚡ 紧急处理 ({len(urgent)}封)")
            for e in urgent:
                s = e["from"].split("<")[0].strip()[:14]
                lines.append(f"    - [{s}] {e['subject']}")

        if needs_reply:
            lines.append(f"\n  📌 待回复 ({len(needs_reply)}封)")
            for e in needs_reply:
                s = e["from"].split("<")[0].strip()[:14]
                lines.append(f"    - [{s}] {e['subject']}")

        if info:
            lines.append(f"\n  📖 仅供参考 ({len(info)}封)")
            for e in info:
                s = e["from"].split("<")[0].strip()[:14]
                lines.append(f"    - [{s}] {e['subject']}")

        total = len(emails)
        lines.append(f"\n  {'='*50}")
        lines.append(f"  📊 统计: 共{total}封 | 紧急{len(urgent)} | 待回复{len(needs_reply)}")
        lines.append(f"  💡 输入 reply <ID> <内容> 回复邮件")
        return "\n".join(lines)

    def _ai_summarize(self, emails: list[dict]) -> str:
        """使用 AI 增强总结。"""
        today_str = date.today().isoformat()
        email_text = "\n".join(
            f"[{i}] From:{e['from']} Subject:{e['subject']}\nBody:{e['body'][:200]}"
            for i, e in enumerate(emails, 1)
        )

        if Config.GEMINI_API_KEY:
            import google.generativeai as genai
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel(Config.GEMINI_MODEL)
            prompt = (
                f"帮我总结以下{len(emails)}封邮件。分类为:⚡紧急处理/📌待回复/📖仅供参考。"
                f"每封邮件用一句话概括核心。\n\n{email_text}"
            )
            resp = model.generate_content(prompt)
            return f"  🤖 AI 增强总结 ({Config.ai_label()})\n{resp.text}"

        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        prompt = (
            f"总结以下{len(emails)}封邮件。按⚡紧急/📌待回复/📖参考分类，每封一句话概括。"
            f"\n\n{email_text}"
        )
        resp = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "system", "content": "你是邮件总结助手。"},
                      {"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=2000,
        )
        return f"  🤖 AI 增强总结 ({Config.ai_label()})\n{resp.choices[0].message.content}"

    def _no_emails_report(self) -> str:
        today_str = date.today().isoformat()
        return (
            f"  {'='*50}\n"
            f"  今日邮件总结 ({today_str})\n"
            f"  {'='*50}\n\n"
            f"  🎉 暂无新邮件！\n"
        )

    def _save_summary(self, report: str) -> None:
        SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
        path = SUMMARY_DIR / f"summary_{date.today().isoformat()}.md"
        try:
            path.write_text(report, encoding="utf-8")
        except Exception:
            pass


def get_today_summary(preferences: dict | None = None) -> str:
    return EmailSummarizer(preferences).summarize_today()
