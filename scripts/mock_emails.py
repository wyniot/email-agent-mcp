"""mock_emails.py - 模拟邮件数据（用于安全测试）

提供不同类型、不同紧急程度的模拟邮件，覆盖以下场景：
- ⚡ 紧急邮件（系统故障、截止日期等）
- 📌 待回复邮件（需确认、讨论、审批等）
- 📖 仅供参考邮件（公告、通知、周报等）
"""

from datetime import date
from typing import Any


def load_mock_emails(folder: str = "INBOX", limit: int = 10) -> list[dict[str, Any]]:
    """返回模拟邮件列表。

    Args:
        folder: 文件夹名（模拟模式下忽略）。
        limit: 最大邮件数。

    Returns:
        邮件字典列表，包含 id / from / subject / body / date / urgency。
    """
    today = date.today().isoformat()
    yesterday = date(2026, 6, 9).isoformat()

    mock_data = [
        # ⚡ 紧急邮件
        {
            "id": "E001",
            "from": "运维中心 <ops@company.com>",
            "subject": "【紧急】线上数据库主从同步延迟告警",
            "body": (
                "各位负责人，\n\n"
                "监测到线上数据库主从同步延迟已超过 30 分钟，可能影响部分读服务。"
                "请相关同事立即排查原因并处理。当前延迟: 1872 秒。\n\n"
                "收到请回复确认。\n运维中心"
            ),
            "date": f"{today} 09:15",
            "urgency": "urgent",
        },
        {
            "id": "E002",
            "from": "客户成功部 <cs@partner.com>",
            "subject": "【重要】客户 A 反馈系统无法登录，请紧急处理",
            "body": (
                "技术团队，\n\n"
                "刚刚接到客户 A 的电话，他们反映从今天早上 8 点开始就无法登录系统，"
                "页面一直显示 502 错误。这是 VIP 客户，请优先排查并回复处理方案。\n\n"
                "客户对接人: 李总 (138xxxxxx)\n紧急程度: P0\n\n"
                "客户成功部"
            ),
            "date": f"{today} 08:50",
            "urgency": "urgent",
        },
        # 📌 待回复邮件
        {
            "id": "003",
            "from": "合作伙伴 <zhang_san@partner-company.com>",
            "subject": "项目进度确认 - Q3 交付计划",
            "body": (
                "您好，\n\n"
                "关于我们正在合作的数据平台项目，想确认一下当前 Q3 的交付计划。"
                "客户那边希望我们在 8 月底前完成第一阶段上线，目前整体进度如何？"
                "是否有需要我方协调的资源？\n\n"
                "盼复。\n张三\n技术总监 - 合作伙伴公司"
            ),
            "date": f"{today} 10:30",
            "urgency": "reply",
        },
        {
            "id": "004",
            "from": "财务部 <caiwu@company.com>",
            "subject": "报销单据审核问题（编号 EXP-2026-0615）",
            "body": (
                "您好，\n\n"
                "上周提交的差旅报销单据（编号 EXP-2026-0615）显示仍在审核中，"
                "请问是否缺少什么材料？机票和住宿发票已全部上传，如有问题请告知。\n\n"
                "感谢！\n李娜 - 财务部"
            ),
            "date": f"{today} 14:15",
            "urgency": "reply",
        },
        {
            "id": "005",
            "from": "供应商 <service@vendor-supplier.com>",
            "subject": "关于续约合同的讨论 - 建议下周沟通",
            "body": (
                "尊敬的负责人，\n\n"
                "我们双方当前的服务合同将于 2026 年 8 月 31 日到期。"
                "如贵司有意续约，我方建议在下周四（6 月 18 日）下午安排一次线上沟通，"
                "讨论新一期的合作条款和价格调整方案。\n\n"
                "请问您什么时候方便？\n\n"
                "供应商服务部"
            ),
            "date": f"{today} 11:45",
            "urgency": "reply",
        },
        # 📖 仅供参考
        {
            "id": "006",
            "from": "技术部 <tech-weekly@company.com>",
            "subject": "【技术周报】第 24 期 - 本周要点",
            "body": (
                "各位同事好，\n\n"
                "以下是本周技术部周报要点：\n"
                "1. 项目 A 已完成 80%，预计 3 天后交付\n"
                "2. 项目 B 因依赖方接口延迟，预计延期 1 周\n"
                "3. 新 CI/CD 流水线已上线，构建时间缩短 40%\n"
                "4. 下周一开始新的代码评审流程\n\n"
                "详见附件。\n编辑: 王伟"
            ),
            "date": f"{today} 09:00",
            "urgency": "info",
        },
        {
            "id": "007",
            "from": "人力资源部 <hr@company.com>",
            "subject": "6 月员工生日会 & 团建活动通知",
            "body": (
                "各位同事好，\n\n"
                "6 月的员工生日会定于本周五（6 月 12 日）下午 4 点在 3 楼休息区举行。"
                "本月共有 8 位寿星，届时会有蛋糕和小礼品。\n\n"
                "另：本季度团建活动定于 6 月 20 日（周六），"
                "地点为郊区温泉度假村，具体安排稍后邮件通知。\n\n"
                "人力资源部"
            ),
            "date": f"{today} 08:00",
            "urgency": "info",
        },
        {
            "id": "008",
            "from": "行业资讯 <newsletter@tech-daily.com>",
            "subject": "AI 日报：GPT-5 发布在即 & 开源大模型最新进展",
            "body": (
                "读者您好，\n\n"
                "今日 AI 领域要闻：\n"
                "1. OpenAI 被曝正在训练 GPT-5，预计年底发布\n"
                "2. Meta 开源 Llama 4，性能接近 GPT-4\n"
                "3. 国内多家厂商跟进降价，API 调用成本下降 60%\n"
                "4. AI Agent 框架生态走向成熟\n\n"
                "查看全文 → https://tech-daily.com/ai-20260610\n\n"
                "科技日报 编辑部"
            ),
            "date": f"{today} 07:30",
            "urgency": "info",
        },
        # 昨日邮件（用于对比）
        {
            "id": "009",
            "from": "技术部 <tech-lead@company.com>",
            "subject": "代码审查通知 - PR #892",
            "body": (
                "请相关同事今天内完成 PR #892 的代码审查。\n"
                "涉及模块: 用户认证系统改造\n"
                "审查人: 张工、李工\n\n"
                "技术部"
            ),
            "date": f"{yesterday} 16:20",
            "urgency": "reply",
        },
        {
            "id": "010",
            "from": "行政部 <admin@company.com>",
            "subject": "办公室搬迁计划 - 新址已确定",
            "body": (
                "各位同事，\n\n"
                "办公室搬迁计划已确定：\n"
                "- 新地址: 科技园区 B 栋 12-15 层\n"
                "- 搬迁日期: 7 月 1 日\n"
                "- 搬迁期间远程办公\n\n"
                "详情请查看附件。\n行政部"
            ),
            "date": f"{yesterday} 10:00",
            "urgency": "info",
        },
    ]
    return mock_data[:limit]


def print_mock_email(email: dict[str, str]) -> None:
    """打印单封模拟邮件的详细信息。"""
    urgency_tag = {"urgent": "⚡紧急", "reply": "📌待回复", "info": "📖仅供参考"}.get(
        email.get("urgency", "info"), "📖"
    )
    print(f"\n{'='*60}")
    print(f"  {urgency_tag}  ID: {email['id']}")
    print(f"  From:    {email['from']}")
    print(f"  Subject: {email['subject']}")
    print(f"  Date:    {email['date']}")
    print(f"{'-'*60}")
    print(f"{email['body']}")
    print(f"{'='*60}\n")


def print_email_list(emails: list[dict]) -> None:
    """以列表形式打印邮件（简洁模式）。"""
    if not emails:
        print("  收件箱为空。")
        return

    for i, e in enumerate(emails, 1):
        urgency_tag = {"urgent": "⚡", "reply": "📌", "info": "📖"}.get(
            e.get("urgency", "info"), "📖"
        )
        sender_short = e["from"].split("<")[0].strip()[:16]
        print(f"  {urgency_tag} [{i:2d}] {e['id']:6s} | {sender_short:16s} | {e['subject']}")
