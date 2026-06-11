"""agent.py - Email Agent 核心逻辑

架构：
- Codex / CLI → agent.run() → 规则引擎（始终可用）+ 可选 AI 增强
- AI 后端（OpenAI / Gemini）为可选项，无 API Key 时一切正常工作
- Python 脚本是「工具层」，Codex 通过 SKILL.md 提供智能
"""

import sys
from typing import Any

from config import Config, UserPreferences
from memory import EmailMemory
from tools import (
    read_emails,
    send_email,
    save_draft,
    list_folders,
    get_inbox_stats,
    format_email_list,
)
from summarizer import EmailSummarizer


# ---------------------------------------------------------------------------
# 回复草稿生成（规则引擎 / AI 增强）
# ---------------------------------------------------------------------------

def _draft_reply(
    email: dict,
    instruction: str = "",
    tone: str = "正式",
) -> str:
    """基于规则生成回复草案。如果 AI 可用则用 AI 增强。

    Args:
        email: 要回复的邮件。
        instruction: 用户对回复内容的指示。
        tone: 回复语气。

    Returns:
        回复文本。
    """
    tone_prefix = {"正式": "您好，\n\n", "友好": "你好！\n\n", "简洁": ""}.get(tone, "您好，\n\n")
    tone_suffix = {"正式": "\n\n祝好，", "友好": "\n\n祝好！", "简洁": ""}.get(tone, "\n\n祝好，")

    sig = UserPreferences.get_signature()
    sig_block = f"\n{sig}" if sig else ""

    # 如果有 AI 增强，尝试用 AI 生成更好的回复
    if Config.ai_available():
        try:
            return _ai_draft_reply(email, instruction, tone)
        except Exception as e:
            print(f"  [Agent] AI 回复生成失败，使用规则回退: {e}")

    # 规则引擎回退
    sender = email.get("from", "").split("<")[0].strip()
    subject = email.get("subject", "")
    body = email.get("body", "")

    reply_body = f"{tone_prefix}感谢您的邮件。"

    if instruction:
        reply_body += f"\n关于您提到的{subject}，{instruction}。"
    elif any(k in subject for k in ["确认", "进度", "计划"]):
        reply_body += f"\n关于{subject}，我们正在积极推进，稍后会给您详细回复。"
    elif any(k in subject for k in ["报销", "审批", "申请"]):
        reply_body += f"\n您的申请已收到，正在处理中，请耐心等待。"
    elif any(k in subject for k in ["合同", "续约", "合作"]):
        reply_body += f"\n感谢您的提议，我们会尽快安排相关同事与您沟通。"
    else:
        reply_body += f"\n已收到您的邮件，我们会尽快处理。"

    reply_body += f"{tone_suffix}{sig_block}"
    return reply_body


def _ai_draft_reply(email: dict, instruction: str, tone: str) -> str:
    """用 AI 后端生成更智能的回复。"""
    if Config.GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        prompt = (
            f"请根据以下邮件起草一封{tone}语气的中文回复。\n\n"
            f"原始邮件:\n发件人: {email['from']}\n"
            f"主题: {email['subject']}\n内容: {email['body'][:500]}\n\n"
            f"回复要点: {instruction}\n\n"
            f"请只输出回信正文，不要前缀说明。"
        )
        resp = model.generate_content(prompt)
        return resp.text

    # OpenAI
    from openai import OpenAI
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=Config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": f"你是邮件助手，用{tone}语气回复邮件。"},
            {"role": "user", "content": (
                f"原始邮件:\nFrom: {email['from']}\n"
                f"Subject: {email['subject']}\nBody: {email['body'][:500]}\n\n"
                f"回复要点: {instruction}\n\n请只输出回信正文。"
            )},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content or "(AI 未生成内容)"


# ---------------------------------------------------------------------------
# Agent 类
# ---------------------------------------------------------------------------

class EmailAgent:
    """Email Agent 主类。

    核心设计：
    - 所有功能在无 API Key 下正常工作（规则引擎）
    - 如果配置了 API Key，启用 AI 增强
    - 作为 Codex Skill 使用时，Codex 通过 SKILL.md 获得智能
    """

    def __init__(self):
        self.memory = EmailMemory()
        self.summarizer = EmailSummarizer(UserPreferences.load())
        self.ai_available = Config.ai_available()

        if self.ai_available:
            print(f"  [Agent] 🤖 AI 增强已启用: {Config.ai_label()}")
        else:
            print(f"  [Agent] ⚙️  规则引擎模式（无 API Key，所有功能正常工作）")

    def run(self, user_input: str) -> str:
        """处理用户指令。

        Args:
            user_input: 自然语言指令。

        Returns:
            处理结果文本。
        """
        print(f"\n  🤖 [Agent] 处理: {user_input}")
        print(f"  {'='*50}")

        # 如果 AI 可用，尝试用 AI 理解并执行
        if self.ai_available:
            result = self._run_with_ai(user_input)
            if result:
                print(f"  {'='*50}")
                return result

        # AI 不可用或失败 → 规则引擎处理
        result = self._run_fallback(user_input)
        print(f"  {'='*50}")
        return result

    def _run_with_ai(self, instruction: str) -> str | None:
        """用 AI 后端处理指令。失败返回 None 触发回退。"""
        try:
            if Config.GEMINI_API_KEY:
                return self._call_gemini(instruction)
            return self._call_langchain(instruction)
        except Exception as e:
            print(f"  [Agent] \u26A0️  AI 处理失败: {e}")
            return None

    def _call_langchain(self, instruction: str) -> str:
        """调用 LangChain 后端。"""
        from langchain.agents import AgentExecutor, create_openai_tools_agent
        from langchain_openai import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.tools import tool as langchain_tool

        tone = UserPreferences.get_reply_tone()
        auto_send = UserPreferences.get_auto_send()
        sig = UserPreferences.get_signature()

        system = (
            f"你是一个邮件处理助手。使用{tone}语气回复。"
            + ("可以直接发送邮件（用户已授权）。" if auto_send else "只保存草稿，不要自动发送。")
            + (f"\n签名: {sig}" if sig else "")
        )

        @langchain_tool
        def lc_read(folder: str = "INBOX", limit: int = 10) -> str:
            """Read emails from a folder."""
            return format_email_list(read_emails(folder, limit), folder)

        @langchain_tool
        def lc_send(to: str, subject: str, body: str) -> str:
            """Send an email."""
            return send_email(to, subject, body)

        @langchain_tool
        def lc_draft(to: str, subject: str, body: str) -> str:
            """Save an email as draft."""
            return save_draft(to, subject, body)

        @langchain_tool
        def lc_folders() -> str:
            """List email folders."""
            return f"📁 {', '.join(list_folders())}"

        tools = [lc_read, lc_send, lc_draft, lc_folders]
        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])

        llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.3,
        )
        agent = create_openai_tools_agent(llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent, tools=tools,
            memory=self.memory._retriever if self.memory._use_vector else None,
            verbose=True, handle_parsing_errors=True,
        )
        result = executor.invoke({"input": instruction})
        return result.get("output", str(result))

    def _call_gemini(self, instruction: str) -> str:
        """调用 Gemini 后端。"""
        import google.generativeai as genai
        genai.configure(api_key=Config.GEMINI_API_KEY)
        tone = UserPreferences.get_reply_tone()
        sig = UserPreferences.get_signature()

        model = genai.GenerativeModel(
            Config.GEMINI_MODEL,
            system_instruction=f"你是邮件助手，用{tone}语气。{('签名: '+sig) if sig else ''}",
        )
        chat = model.start_chat()
        resp = chat.send_message(instruction)
        return resp.text

    def _run_fallback(self, instruction: str) -> str:
        """规则引擎处理指令（无 AI 时使用）。

        支持的命令:
        - read, summary, list, reply <id> <text>, help
        """
        cmd = instruction.lower().strip()

        if cmd == "summary":
            return self.summarize_today()

        if cmd == "read":
            emails = read_emails()
            stats = get_inbox_stats(emails)
            result = format_email_list(emails, "收件箱")
            result += (
                f"\n  📊 统计: 共{stats['total']}封 | "
                f"⚡紧急{len(stats['urgent'])} | "
                f"📌待回复{len(stats['reply'])} | "
                f"📖参考{len(stats['info'])}"
            )
            return result

        if cmd == "list":
            return f"📁 文件夹: {', '.join(list_folders())}"

        if cmd.startswith("reply "):
            parts = cmd[6:].strip().split(" ", 1)
            ref = parts[0]
            instr = parts[1] if len(parts) > 1 else ""
            emails = read_emails()
            target = None
            if ref.isdigit():
                idx = int(ref) - 1
                if 0 <= idx < len(emails):
                    target = emails[idx]
            if not target:
                target = next((e for e in emails if e["id"] == ref), None)
            if not target:
                return "!! 没导入" + ref
            reply = _draft_reply(target, instr, UserPreferences.get_reply_tone())
            tone = UserPreferences.get_reply_tone()
            result = (
                f"📝 回复草稿（{tone}语气）:\n\n{reply}\n\n"
                f"---\n原始邮件: [{target['id']}] {target['subject']} - {target['from']}"
            )
            # 保存到记忆
            self.memory.save_interaction(email_id, target["subject"], instr, reply)
            return result

        if cmd == "history":
            return self.get_memory_summary()

        return (
            f"好的，我收到了你的指令。\n"
            f"当前可执行命令: summary / read / list / reply <ID> <内容> / history\n"
            f"如需更智能的处理，请在 .env 中配置 API Key。"
        )

    # ------------------------------------------------------------------
    # 便捷方法
    # ------------------------------------------------------------------

    def summarize_today(self, max_emails: int = 20) -> str:
        """生成今日邮件总结。"""
        print(f"\n  📋 正在生成今日邮件总结...")
        return self.summarizer.summarize_today(max_emails)

    def get_memory_summary(self) -> str:
        """获取处理历史。"""
        history = self.memory.get_history(10)
        if not history:
            return "暂无处理历史。"
        lines = ["近期处理记录:\n"]
        for h in history:
            lines.append(f"  [{h['email_id']}] {h['subject']}")
            lines.append(f"      回复: {h['reply'][:80]}...")
        return "\n".join(lines)
