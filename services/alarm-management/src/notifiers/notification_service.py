"""
通知服务
统一管理各种通知渠道
"""
from typing import List, Dict, Any
from loguru import logger

from .email_notifier import EmailNotifier
from .sms_notifier import SMSNotifier
from ..config.constants import NotificationChannelEnum


class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.sms_notifier = SMSNotifier()
        
        # 收件人配置（可从数据库读取）
        self.recipients_config = {
            "WARNING": {
                "emails": ["engineer@example.com"],
                "phones": []
            },
            "ALARM": {
                "emails": ["engineer@example.com", "supervisor@example.com"],
                "phones": ["13800138000"]
            },
            "CRITICAL": {
                "emails": ["engineer@example.com", "supervisor@example.com", "manager@example.com"],
                "phones": ["13800138000", "13900139000"]
            }
        }
    
    async def send_alarm_notification(
        self,
        alarm_data: dict,
        channels: List[str] = None
    ) -> Dict[str, bool]:
        """
        发送报警通知
        
        Args:
            alarm_data: 报警数据
            channels: 通知渠道列表（None表示使用默认配置）
        
        Returns:
            各渠道发送结果
        """
        alarm_level = alarm_data.get("alarm_level", "WARNING")
        
        # 使用默认渠道配置
        if channels is None:
            if alarm_level == "WARNING":
                channels = ["EMAIL", "WEBSOCKET"]
            elif alarm_level == "ALARM":
                channels = ["EMAIL", "SMS", "WEBSOCKET"]
            else:  # CRITICAL
                channels = ["EMAIL", "SMS", "WEBSOCKET"]
        
        results = {}
        
        # 发送邮件
        if "EMAIL" in channels:
            recipients = self.recipients_config.get(alarm_level, {}).get("emails", [])
            if recipients:
                results["EMAIL"] = await self.email_notifier.send_alarm_notification(
                    recipients,
                    alarm_data
                )
        
        # 发送短信
        if "SMS" in channels:
            recipients = self.recipients_config.get(alarm_level, {}).get("phones", [])
            if recipients:
                results["SMS"] = await self.sms_notifier.send_alarm_notification(
                    recipients,
                    alarm_data
                )
        
        # WebSocket通知由WebSocket管理器处理
        if "WEBSOCKET" in channels:
            results["WEBSOCKET"] = True  # 实际发送在WebSocket管理器中
        
        logger.info(f"报警通知发送完成: {results}")
        return results
    
    async def send_custom_notification(
        self,
        channels: List[str],
        recipients: List[str],
        message: str,
        subject: str = None
    ) -> Dict[str, bool]:
        """
        发送自定义通知
        
        Args:
            channels: 通知渠道列表
            recipients: 接收人列表
            message: 消息内容
            subject: 主题（用于邮件）
        
        Returns:
            各渠道发送结果
        """
        results = {}
        
        # 发送邮件
        if "EMAIL" in channels and subject:
            results["EMAIL"] = await self.email_notifier.send(
                recipients,
                subject,
                message
            )
        
        # 发送短信
        if "SMS" in channels:
            results["SMS"] = await self.sms_notifier.send(
                recipients,
                {"message": message}
            )
        
        return results