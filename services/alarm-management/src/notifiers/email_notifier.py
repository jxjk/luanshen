"""
邮件通知器
"""
import aiosmtplib
from email.message import EmailMessage
from typing import Optional, List
import asyncio
from loguru import logger

from ..config.settings import settings


class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from = settings.smtp_from
        self.smtp_use_tls = settings.smtp_use_tls
    
    async def send(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        发送邮件
        
        Args:
            recipients: 收件人列表
            subject: 邮件主题
            body: 邮件内容
            html: 是否为HTML格式
        
        Returns:
            是否发送成功
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("邮件配置未设置，跳过邮件发送")
            return False
        
        try:
            # 创建邮件消息
            message = EmailMessage()
            message["From"] = self.smtp_from
            message["To"] = ", ".join(recipients)
            message["Subject"] = subject
            
            # 设置邮件内容
            if html:
                message.add_alternative(body, subtype="html")
            else:
                message.set_content(body)
            
            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls,
                timeout=10
            )
            
            logger.info(f"邮件发送成功: {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False
    
    async def send_alarm_notification(
        self,
        recipients: List[str],
        alarm_data: dict
    ) -> bool:
        """
        发送报警通知邮件
        
        Args:
            recipients: 收件人列表
            alarm_data: 报警数据
        
        Returns:
            是否发送成功
        """
        # 构建邮件主题
        level_emoji = {
            "WARNING": "⚠️",
            "ALARM": "🔔",
            "CRITICAL": "🚨"
        }
        emoji = level_emoji.get(alarm_data.get("alarm_level", "WARNING"), "⚠️")
        subject = f"{emoji} 报警通知 - 设备 {alarm_data.get('device_id')} - {alarm_data.get('alarm_code')}"
        
        # 构建HTML邮件内容
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f44336; color: white; padding: 15px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .info {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
                .footer {{ margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>设备报警通知</h2>
                </div>
                <div class="content">
                    <div class="info">
                        <span class="label">设备ID：</span>{alarm_data.get('device_id')}
                    </div>
                    <div class="info">
                        <span class="label">报警级别：</span>{alarm_data.get('alarm_level')}
                    </div>
                    <div class="info">
                        <span class="label">报警代码：</span>{alarm_data.get('alarm_code')}
                    </div>
                    <div class="info">
                        <span class="label">报警消息：</span>{alarm_data.get('alarm_message')}
                    </div>
                    <div class="info">
                        <span class="label">发生时间：</span>{alarm_data.get('created_at')}
                    </div>
                </div>
                <div class="footer">
                    <p>请及时处理此报警事件。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send(recipients, subject, html_body, html=True)