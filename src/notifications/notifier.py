"""通知功能模块"""

import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from ..analytics.net_value_analyzer import NetValueChange, BonusPeriod
from ..models.product import Product

logger = logging.getLogger(__name__)
DAYS_PER_YEAR = 365


@dataclass
class NotificationMessage:
    """通知消息"""
    subject: str
    body: str
    recipient: Optional[str] = None


class Notifier(ABC):
    """通知器抽象基类"""

    @abstractmethod
    def send(self, message: NotificationMessage) -> bool:
        """发送通知

        Args:
            message: 通知消息

        Returns:
            是否发送成功
        """
        pass


class EmailNotifier(Notifier):
    """邮件通知器

    使用 SMTP 发送邮件通知。
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str,
        use_tls: bool = True
    ):
        """初始化邮件通知器

        Args:
            smtp_host: SMTP 服务器地址
            smtp_port: SMTP 端口
            username: 用户名
            password: 密码
            from_addr: 发件人地址
            use_tls: 是否使用 TLS
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.use_tls = use_tls

    def send(self, message: NotificationMessage) -> bool:
        """发送邮件

        Args:
            message: 通知消息

        Returns:
            是否发送成功
        """
        if not message.recipient:
            logger.warning("没有指定收件人，跳过发送")
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = self.from_addr
            msg["To"] = message.recipient
            msg["Subject"] = message.subject

            # 添加正文
            msg.attach(MIMEText(message.body, "plain", "utf-8"))

            # 发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"邮件已发送: {message.subject} -> {message.recipient}")
            return True

        except (smtplib.SMTPException, ConnectionError, TimeoutError) as e:
            logger.error(f"邮件发送失败: {type(e).__name__}: {e}", exc_info=True)
            return False


class ProductNotifier:
    """产品通知管理器

    用于生成和发送各种产品相关通知。
    """

    def __init__(self, notifier: Notifier):
        """初始化通知管理器

        Args:
            notifier: 底层通知器（如邮件通知器）
        """
        self.notifier = notifier

    def notify_new_products(
        self,
        new_products: List[Product],
        recipient: str
    ) -> bool:
        """通知新增产品

        Args:
            new_products: 新增产品列表
            recipient: 收件人

        Returns:
            是否发送成功
        """
        if not new_products:
            logger.info("没有新增产品，跳过通知")
            return True

        lines = [
            f"发现 {len(new_products)} 个新增理财产品",
            "",
            "=" * 60,
            f"{'产品名称':<30} {'代码':<15} {'银行':<10} {'净值':>10}",
            "-" * 70,
        ]

        for p in new_products[:20]:  # 限制显示数量
            net_value_str = f"{p.net_value:.4f}" if p.net_value else "-"
            lines.append(f"{p.name:<28} {p.code:<15} {p.bank:<10} {net_value_str:>10}")

        if len(new_products) > 20:
            lines.append(f"... 还有 {len(new_products) - 20} 个产品")

        lines.append("=" * 60)

        message = NotificationMessage(
            subject=f"【B2 系统】发现 {len(new_products)} 个新增理财产品",
            body="\n".join(lines),
            recipient=recipient,
        )

        return self.notifier.send(message)

    def notify_high_growth_products(
        self,
        high_growth: List[NetValueChange],
        recipient: str,
        threshold: float = 1.0
    ) -> bool:
        """通知高增长产品

        Args:
            high_growth: 高增长产品列表
            recipient: 收件人
            threshold: 增长率阈值

        Returns:
            是否发送成功
        """
        if not high_growth:
            logger.info("没有高增长产品，跳过通知")
            return True

        lines = [
            f"发现 {len(high_growth)} 个高增长理财产品（单日 >= {threshold}%）",
            "",
            "=" * 70,
            f"{'产品名称':<30} {'代码':<12} {'银行':<10} {'前值':>10} {'现值':>10} {'涨跌':>10}",
            "-" * 85,
        ]

        for c in high_growth[:20]:
            direction = "+" if c.change_percent > 0 else ""
            lines.append(
                f"{c.product_name:<28} {c.product_code:<12} {c.bank:<10} "
                f"{c.previous_value:>10.4f} {c.current_value:>10.4f} {direction}{c.change_percent:>9.2f}%"
            )

        if len(high_growth) > 20:
            lines.append(f"... 还有 {len(high_growth) - 20} 个产品")

        lines.append("=" * 70)

        message = NotificationMessage(
            subject=f"【B2 系统】发现 {len(high_growth)} 个高增长理财产品",
            body="\n".join(lines),
            recipient=recipient,
        )

        return self.notifier.send(message)

    def notify_bonus_periods(
        self,
        bonus_periods: List[BonusPeriod],
        recipient: str
    ) -> bool:
        """通知红利期产品

        Args:
            bonus_periods: 红利期产品列表
            recipient: 收件人

        Returns:
            是否发送成功
        """
        active = [b for b in bonus_periods if b.is_active]

        if not active:
            logger.info("没有处于红利期的产品，跳过通知")
            return True

        lines = [
            f"发现 {len(active)} 个产品处于红利期",
            "",
            "=" * 80,
            f"{'产品名称':<30} {'代码':<12} {'银行':<10} {'收益率':>10} {'天数':>6} {'年化':>10}",
            "-" * 80,
        ]

        for b in sorted(active, key=lambda x: x.total_return, reverse=True)[:20]:
            lines.append(
                f"{b.product_name:<28} {b.product_code:<12} {b.bank:<10} "
                f"{b.total_return:>9.2f}% {b.days_since_start:>5}天 {b.annualized_return:>9.2f}%"
            )

        if len(active) > 20:
            lines.append(f"... 还有 {len(active) - 20} 个产品")

        lines.append("")
        lines.append("红利期说明：产品上市初期（30天内）收益率超过 0.5% 被视为红利期")
        lines.append("=" * 80)

        message = NotificationMessage(
            subject=f"【B2 系统】发现 {len(active)} 个产品处于红利期",
            body="\n".join(lines),
            recipient=recipient,
        )

        return self.notifier.send(message)

    def notify_error(
        self,
        error_message: str,
        recipient: str,
        context: Optional[str] = None
    ) -> bool:
        """通知系统错误

        Args:
            error_message: 错误信息
            recipient: 收件人
            context: 错误上下文

        Returns:
            是否发送成功
        """
        lines = [
            "【B2 系统错误通知】",
            "",
            f"错误信息: {error_message}",
            f"发生时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        if context:
            lines.append(f"上下文: {context}")

        message = NotificationMessage(
            subject="【B2 系统】错误通知",
            body="\n".join(lines),
            recipient=recipient,
        )

        return self.notifier.send(message)


class ConsoleNotifier(Notifier):
    """控制台通知器（用于测试）

    将通知输出到控制台。
    """

    def send(self, message: NotificationMessage) -> bool:
        """输出通知到控制台

        Args:
            message: 通知消息

        Returns:
            是否成功（始终为 True）
        """
        print("\n" + "=" * 60)
        print(f"主题: {message.subject}")
        print("-" * 60)
        print(message.body)
        print("=" * 60 + "\n")

        logger.info(f"控制台通知: {message.subject}")
        return True
