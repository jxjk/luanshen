"""
短信通知器（阿里云短信）
"""
from typing import List, Dict, Any
from loguru import logger

try:
    from alibabacloud_dysmsapi20170525.client import Client as DysmsClient
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_dysmsapi20170525 import models as dysms_models
    ALIYUN_AVAILABLE = True
except ImportError:
    ALIYUN_AVAILABLE = False
    logger.warning("阿里云SDK未安装，短信功能不可用")


class SMSNotifier:
    """短信通知器"""
    
    def __init__(self):
        if not ALIYUN_AVAILABLE:
            return
        
        self.access_key_id = settings.aliyun_access_key_id
        self.access_key_secret = settings.aliyun_access_key_secret
        self.sign_name = settings.aliyun_sms_sign_name
        self.template_code = settings.aliyun_sms_template_code
        
        # 创建客户端
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        config.endpoint = f'dysmsapi.aliyuncs.com'
        self.client = DysmsClient(config)
    
    async def send(
        self,
        phone_numbers: List[str],
        template_param: Dict[str, Any]
    ) -> bool:
        """
        发送短信
        
        Args:
            phone_numbers: 手机号列表
            template_param: 模板参数
        
        Returns:
            是否发送成功
        """
        if not ALIYUN_AVAILABLE:
            logger.warning("阿里云SDK未安装，跳过短信发送")
            return False
        
        if not self.access_key_id or not self.access_key_secret:
            logger.warning("阿里云短信配置未设置，跳过短信发送")
            return False
        
        try:
            # 构建请求
            send_sms_request = dysms_models.SendSmsRequest(
                sign_name=self.sign_name,
                template_code=self.template_code,
                phone_numbers=','.join(phone_numbers),
                template_param=str(template_param)
            )
            
            # 发送短信
            response = await asyncio.to_thread(
                self.client.send_sms,
                send_sms_request
            )
            
            if response.body.code == 'OK':
                logger.info(f"短信发送成功: {phone_numbers}")
                return True
            else:
                logger.error(f"短信发送失败: {response.body.message}")
                return False
                
        except Exception as e:
            logger.error(f"短信发送失败: {e}")
            return False
    
    async def send_alarm_notification(
        self,
        phone_numbers: List[str],
        alarm_data: dict
    ) -> bool:
        """
        发送报警通知短信
        
        Args:
            phone_numbers: 手机号列表
            alarm_data: 报警数据
        
        Returns:
            是否发送成功
        """
        # 构建模板参数
        template_param = {
            "device_id": str(alarm_data.get('device_id', '')),
            "alarm_level": str(alarm_data.get('alarm_level', '')),
            "alarm_code": str(alarm_data.get('alarm_code', '')),
            "time": alarm_data.get('created_at', '')[:19] if alarm_data.get('created_at') else ''
        }
        
        return await self.send(phone_numbers, template_param)


# 导入settings
from ..config.settings import settings