# DeepSeek 大模型集成说明

## 📋 概述

本系统已集成 DeepSeek 大语言模型（LLM），用于生成智能优化建议和审查分析报告。

## 🚀 功能特性

### 1. 智能优化建议
- 基于材料、刀具、机床参数生成个性化优化建议
- 提供转速、进给、切深、切宽的具体优化方向
- 生成综合优化建议和风险提示

### 2. 审查分析报告
- 安全性分析：解释安全评分的依据
- 风险分析：识别主要风险点
- 改进建议：提供具体的改进措施
- 专家点评：专业角度的评估

## 🔧 配置方法

### 方法一：环境变量（推荐）

#### Windows
```cmd
set DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

#### PowerShell
```powershell
$env:DEEPSEEK_API_KEY="your_deepseek_api_key_here"
```

#### Linux/Mac
```bash
export DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 方法二：.env 文件

在项目根目录或 `services/parameter-optimization/` 目录下的 `.env` 文件中添加：

```env
# DeepSeek LLM 配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.7
DEEPSEEK_MAX_TOKENS=2000
DEEPSEEK_TIMEOUT=30
DEEPSEEK_ENABLED=true
```

## 📝 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥（必需） | - |
| `DEEPSEEK_BASE_URL` | DeepSeek API 基础 URL | https://api.deepseek.com/v1 |
| `DEEPSEEK_MODEL` | 使用的模型名称 | deepseek-chat |
| `DEEPSEEK_TEMPERATURE` | 温度参数（0-1，越高越随机） | 0.7 |
| `DEEPSEEK_MAX_TOKENS` | 最大生成令牌数 | 2000 |
| `DEEPSEEK_TIMEOUT` | 请求超时时间（秒） | 30 |
| `DEEPSEEK_ENABLED` | 是否启用 LLM 功能 | true |

## 🧪 测试集成

### 运行测试脚本

```bash
cd services/parameter-optimization
python test_deepseek.py
```

### 测试内容
1. ✅ API 连接测试
2. ✅ 优化建议生成测试
3. ✅ 审查分析生成测试

## 💡 使用方式

### API 调用

```bash
POST /api/v1/optimization/ai-optimize?enable_llm=true
Content-Type: application/json

{
  "material_id": "P1",
  "tool_id": "1",
  "machine_id": "1",
  "strategy_id": "1",
  "population_size": 10240,
  "generations": 200
}
```

### 响应示例

```json
{
  "success": true,
  "message": "AI 规划已完成；AI 审查评分：85.5/100",
  "result": {
    "speed": 3200.0,
    "feed": 640.0,
    ...
  },
  "ai_planning": {
    "search_range": {...},
    "reason": "...",
    "safety_factor": 0.85,
    "suggestions": {
      "speed": "材料硬度较高，建议降低转速以提高刀具寿命",
      "feed": "硬质合金刀具可承受较高进给，建议在推荐范围内选择较大值",
      "general": "优化参数基本合理，建议在实际加工中根据情况进行微调",
      "risks": "请注意监控刀具磨损情况，定期检查加工质量"
    }
  },
  "ai_review": {
    "passed": true,
    "safety_score": 85.5,
    "overall_assessment": "存在警告：参数基本合理，但有改进空间",
    "summary": {...},
    "items": [...],
    "llm_analysis": "【参数优化审查报告】\n\n一、安全性分析..."
  }
}
```

## 🔍 工作原理

### 1. 优化建议生成流程

```
用户请求 → 收集参数信息 → 构建 Prompt → 调用 DeepSeek API → 解析响应 → 返回建议
```

### 2. 审查分析生成流程

```
优化结果 → 审查结果统计 → 构建 Prompt → 调用 DeepSeek API → 生成报告 → 返回分析
```

## ⚠️ 注意事项

1. **API Key 安全**
   - 不要将 API Key 提交到代码仓库
   - 使用环境变量或 .env 文件管理
   - 定期轮换 API Key

2. **网络要求**
   - 需要能够访问 DeepSeek API 服务器
   - 确保网络连接稳定
   - 注意 API 调用频率限制

3. **性能影响**
   - LLM 调用会增加响应时间（约 2-5 秒）
   - 可以通过 `enable_llm=false` 参数禁用
   - 系统会自动降级到规则建议

4. **成本控制**
   - DeepSeek API 按使用量计费
   - 建议设置合理的 `max_tokens` 限制
   - 监控 API 使用量和费用

## 🛠️ 故障排除

### 问题 1：LLM 功能未启用

**症状**：响应中没有 LLM 建议

**解决方案**：
1. 检查 `DEEPSEEK_API_KEY` 是否正确设置
2. 查看日志中的警告信息
3. 运行测试脚本验证配置

### 问题 2：API 调用超时

**症状**：请求超时或失败

**解决方案**：
1. 增加 `DEEPSEEK_TIMEOUT` 值
2. 检查网络连接
3. 验证 API 服务器状态

### 问题 3：建议质量不佳

**症状**：生成的建议不够专业

**解决方案**：
1. 调整 `DEEPSEEK_TEMPERATURE` 参数
2. 改进 Prompt 设计
3. 提供更详细的上下文信息

## 📚 相关资源

- [DeepSeek 官方文档](https://platform.deepseek.com/docs)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)
- [DeepSeek 控制台](https://platform.deepseek.com/console)

## 📞 支持

如遇到问题，请：
1. 查看日志文件：`logs/app.log`
2. 运行测试脚本：`python test_deepseek.py`
3. 检查 DeepSeek 控制台中的 API 使用情况

---

**最后更新**：2026-02-05
**版本**：1.0.0