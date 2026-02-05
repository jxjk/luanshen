"""
大语言模型服务
支持 DeepSeek 等大语言模型，用于生成智能优化建议
"""
import os
import httpx
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM 配置"""
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30


class LLMService:
    """大语言模型服务"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        初始化 LLM 服务
        
        Args:
            config: LLM 配置，如果为 None 则从环境变量读取
        """
        if config is None:
            config = LLMConfig(
                api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "2000")),
                timeout=int(os.getenv("DEEPSEEK_TIMEOUT", "30"))
            )
        
        self.config = config
        self.enabled = bool(config.api_key)
        
        if not self.enabled:
            logger.warning("DeepSeek API Key 未配置，LLM 功能将不可用")
        else:
            logger.info(f"DeepSeek LLM 服务已初始化: {config.model}")
    
    async def generate_optimization_suggestions(
        self,
        context: Dict
    ) -> Dict[str, str]:
        """
        生成优化建议
        
        Args:
            context: 上下文信息（包含材料、刀具、机床、优化结果等）
        
        Returns:
            优化建议字典
        """
        if not self.enabled:
            return self._generate_fallback_suggestions(context)
        
        try:
            prompt = self._build_optimization_prompt(context)
            response = await self._call_llm(prompt)
            return self._parse_optimization_response(response)
        except Exception as e:
            logger.error(f"LLM 优化建议生成失败: {str(e)}")
            return self._generate_fallback_suggestions(context)
    
    async def generate_review_analysis(
        self,
        params: Dict,
        review_result: Dict
    ) -> str:
        """
        生成审查分析报告
        
        Args:
            params: 优化参数
            review_result: 审查结果
        
        Returns:
            分析报告文本
        """
        if not self.enabled:
            return self._generate_fallback_review(review_result)
        
        try:
            prompt = self._build_review_prompt(params, review_result)
            response = await self._call_llm(prompt)
            return response
        except Exception as e:
            logger.error(f"LLM 审查分析生成失败: {str(e)}")
            return self._generate_fallback_review(review_result)
    
    async def _call_llm(self, prompt: str) -> str:
        """
        调用 LLM API
        
        Args:
            prompt: 提示词
        
        Returns:
            LLM 响应文本
        """
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位资深的数控加工工艺优化专家，擅长刀具参数优化、材料加工特性和机床性能分析。请提供专业、实用、具体的优化建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    def _build_optimization_prompt(self, context: Dict) -> str:
        """构建优化建议提示词"""
        material = context.get("material", {})
        tool = context.get("tool", {})
        machine = context.get("machine", {})
        result = context.get("result", {})
        
        prompt = f"""请为以下数控加工场景提供优化建议：

【材料信息】
- 材料名称：{material.get('name', '未知')}
- 材料组别：{material.get('group', '未知')}
- 硬度：{material.get('hardness', 0)} HB
- 抗拉强度：{material.get('tensile_strength', 0)} MPa
- 可加工性：{material.get('machinability', 0)}

【刀具信息】
- 刀具类型：{tool.get('type', '未知')}
- 刀具材料：{tool.get('material', '未知')}
- 涂层：{tool.get('coating', '无')}
- 直径：{tool.get('diameter', 0)} mm
- 齿数：{tool.get('teeth', 0)}
- 悬伸：{tool.get('overhang', 0)} mm

【机床信息】
- 机床类型：{machine.get('type', '未知')}
- 最大转速：{machine.get('max_spindle_speed', 0)} r/min
- 最大功率：{machine.get('max_power', 0)} kW
- 最大扭矩：{machine.get('max_torque', 0)} Nm

【优化结果】
- 转速：{result.get('speed', 0)} r/min
- 进给：{result.get('feed', 0)} mm/min
- 切深：{result.get('cut_depth', 0)} mm
- 切宽：{result.get('cut_width', 0)} mm
- 切削速度：{result.get('cutting_speed', 0)} m/min
- 每齿进给：{result.get('feed_per_tooth', 0)} mm
- 材料去除率：{result.get('material_removal_rate', 0)} cm³/min
- 刀具寿命：{result.get('tool_life', 0)} min
- 功率：{result.get('power', 0)} kW
- 扭矩：{result.get('torque', 0)} Nm
- 进给力：{result.get('feed_force', 0)} N
- 底面粗糙度：{result.get('bottom_roughness', 0)} μm
- 侧面粗糙度：{result.get('side_roughness', 0)} μm

请针对以下几个方面提供具体建议：
1. 转速优化建议
2. 进给优化建议
3. 切深优化建议
4. 切宽优化建议
5. 综合优化建议
6. 风险提示

请以 JSON 格式返回，格式如下：
{{
    "speed": "转速优化建议",
    "feed": "进给优化建议",
    "cut_depth": "切深优化建议",
    "cut_width": "切宽优化建议",
    "general": "综合优化建议",
    "risks": "风险提示"
}}
"""
        return prompt
    
    def _build_review_prompt(self, params: Dict, review_result: Dict) -> str:
        """构建审查分析提示词"""
        safety_score = review_result.get("safety_score", 0)
        summary = review_result.get("summary", {})
        
        prompt = f"""请为以下参数优化结果提供详细的审查分析报告：

【优化参数】
{json.dumps(params, indent=2, ensure_ascii=False)}

【审查结果】
- 安全评分：{safety_score}/100
- 总体评估：{review_result.get('overall_assessment', '未知')}
- 安全项：{summary.get('safe', 0)}
- 警告项：{summary.get('warning', 0)}
- 错误项：{summary.get('error', 0)}
- 严重错误项：{summary.get('critical', 0)}

请提供以下内容：
1. 安全性分析：解释为什么得到这个安全评分
2. 风险分析：分析存在的主要风险点
3. 改进建议：针对存在的问题提供具体的改进措施
4. 专家点评：从专业角度对优化结果进行点评

请用专业、客观、建设性的语言撰写报告。
"""
        return prompt
    
    def _parse_optimization_response(self, response: str) -> Dict[str, str]:
        """解析 LLM 优化建议响应"""
        try:
            # 尝试解析 JSON
            suggestions = json.loads(response)
            return {
                "speed": suggestions.get("speed", "无法生成转速建议"),
                "feed": suggestions.get("feed", "无法生成进给建议"),
                "cut_depth": suggestions.get("cut_depth", "无法生成切深建议"),
                "cut_width": suggestions.get("cut_width", "无法生成切宽建议"),
                "general": suggestions.get("general", "无法生成综合建议"),
                "risks": suggestions.get("risks", "无法生成风险提示")
            }
        except json.JSONDecodeError:
            # 如果 JSON 解析失败，返回默认建议
            logger.warning("LLM 返回的不是有效的 JSON 格式")
            return self._generate_fallback_suggestions({})
    
    def _generate_fallback_suggestions(self, context: Dict) -> Dict[str, str]:
        """生成备用建议（当 LLM 不可用时）"""
        material = context.get("material", {})
        tool = context.get("tool", {})
        
        suggestions = {}
        
        # 基于材料硬度的转速建议
        hardness = material.get("hardness", 200)
        if hardness > 300:
            suggestions["speed"] = "材料硬度较高，建议降低转速以提高刀具寿命"
        elif hardness < 150:
            suggestions["speed"] = "材料硬度较低，可适当提高转速以提高效率"
        else:
            suggestions["speed"] = "转速设置合理，符合材料加工特性"
        
        # 基于刀具材料的进给建议
        tool_material = tool.get("material", "")
        if "硬质合金" in tool_material:
            suggestions["feed"] = "硬质合金刀具可承受较高进给，建议在推荐范围内选择较大值"
        else:
            suggestions["feed"] = "刀具材料较软，建议适当降低进给以保护刀具"
        
        # 切深建议
        suggestions["cut_depth"] = "切深设置在推荐范围内，可考虑根据加工精度要求微调"
        suggestions["cut_width"] = "切宽设置合理，可根据加工表面质量要求进行调整"
        suggestions["general"] = "优化参数基本合理，建议在实际加工中根据情况进行微调"
        suggestions["risks"] = "请注意监控刀具磨损情况，定期检查加工质量"
        
        return suggestions
    
    def _generate_fallback_review(self, review_result: Dict) -> str:
        """生成备用审查报告（当 LLM 不可用时）"""
        safety_score = review_result.get("safety_score", 0)
        summary = review_result.get("summary", {})
        
        report = f"""
【参数优化审查报告】

一、安全性分析
本次优化结果的安全评分为 {safety_score}/100。
- 安全项：{summary.get('safe', 0)} 个
- 警告项：{summary.get('warning', 0)} 个
- 错误项：{summary.get('error', 0)} 个
- 严重错误项：{summary.get('critical', 0)} 个

二、风险分析
{"存在一定风险，需要关注。" if safety_score < 80 else "参数设置较为安全，风险较低。"}

三、改进建议
建议在实际加工中密切监控刀具磨损情况和机床负载，根据实际情况进行微调。

四、专家点评
{"优化结果存在一些问题，建议重新调整参数。" if safety_score < 70 else "优化结果基本合理，可以投入使用。"}
"""
        return report.strip()


# 全局 LLM 服务实例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取 LLM 服务实例（单例模式）"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service