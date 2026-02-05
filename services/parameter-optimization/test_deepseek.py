"""
DeepSeek LLM 集成测试脚本
测试 DeepSeek API 连接和功能
"""
import os
import asyncio
import sys

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.llm_service import LLMService, LLMConfig


async def test_deepseek_connection():
    """测试 DeepSeek 连接"""
    print("=" * 60)
    print("DeepSeek LLM 集成测试")
    print("=" * 60)
    
    # 检查环境变量
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误：DEEPSEEK_API_KEY 环境变量未设置")
        print("\n请设置环境变量：")
        print("  Windows: set DEEPSEEK_API_KEY=your_api_key_here")
        print("  Linux/Mac: export DEEPSEEK_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ DEEPSEEK_API_KEY 已设置（长度: {len(api_key)}）")
    
    # 初始化 LLM 服务
    config = LLMConfig(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        temperature=0.7,
        max_tokens=2000,
        timeout=30
    )
    
    llm_service = LLMService(config)
    
    if not llm_service.enabled:
        print("❌ LLM 服务未启用")
        return False
    
    print(f"✅ LLM 服务已初始化")
    print(f"   - API Base URL: {config.base_url}")
    print(f"   - Model: {config.model}")
    print(f"   - Temperature: {config.temperature}")
    print(f"   - Max Tokens: {config.max_tokens}")
    
    # 测试优化建议生成
    print("\n" + "=" * 60)
    print("测试 1：生成优化建议")
    print("=" * 60)
    
    test_context = {
        "material": {
            "name": "45号钢",
            "group": "P",
            "hardness": 220,
            "tensile_strength": 600,
            "machinability": 0.8
        },
        "tool": {
            "type": "面铣刀",
            "material": "硬质合金",
            "coating": "TiN",
            "diameter": 50,
            "teeth": 6,
            "overhang": 60
        },
        "machine": {
            "type": "立式加工中心",
            "max_spindle_speed": 8000,
            "max_power": 15,
            "max_torque": 120
        },
        "result": {
            "speed": 2500,
            "feed": 800,
            "cut_depth": 2.0,
            "cut_width": 40,
            "cutting_speed": 392.7,
            "feed_per_tooth": 0.053,
            "material_removal_rate": 64.0,
            "tool_life": 90,
            "power": 8.5,
            "torque": 32.5,
            "feed_force": 1500,
            "bottom_roughness": 1.6,
            "side_roughness": 3.2
        }
    }
    
    try:
        suggestions = await llm_service.generate_optimization_suggestions(test_context)
        print("\n✅ 优化建议生成成功：")
        for key, value in suggestions.items():
            print(f"\n【{key}】")
            print(f"  {value}")
    except Exception as e:
        print(f"\n❌ 优化建议生成失败: {str(e)}")
        return False
    
    # 测试审查分析生成
    print("\n" + "=" * 60)
    print("测试 2：生成审查分析")
    print("=" * 60)
    
    test_review_result = {
        "safety_score": 85.5,
        "overall_assessment": "存在警告：参数基本合理，但有改进空间",
        "summary": {
            "safe": 6,
            "warning": 2,
            "error": 0,
            "critical": 0
        }
    }
    
    try:
        analysis = await llm_service.generate_review_analysis(
            test_context["result"],
            test_review_result
        )
        print("\n✅ 审查分析生成成功：")
        print(analysis)
    except Exception as e:
        print(f"\n❌ 审查分析生成失败: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！DeepSeek 集成正常工作")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_deepseek_connection())
    sys.exit(0 if success else 1)
