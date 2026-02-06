"""
测试参数优化 - 验证约束是否生效
"""
import requests
import json

# 测试数据 - 使用刀具2（Φ35mm牛鼻刀）
test_data = {
    "material_id": "P15",
    "tool_id": "2",
    "machine_id": "1",
    "strategy_id": "1",
    "population_size": 1024,  # 减少种群大小以加快测试
    "generations": 50
}

print("=" * 80)
print("测试参数优化")
print("=" * 80)
print(f"测试数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
print()

# 调用优化 API
try:
    response = requests.post(
        "http://localhost:5007/api/v1/optimization/optimize",
        json=test_data,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        print("优化成功！")
        print()
        print("优化结果:")
        print("=" * 80)
        
        if result.get("result"):
            r = result["result"]
            print(f"转速: {r.get('speed', 0):.2f} r/min")
            print(f"进给: {r.get('feed', 0):.2f} mm/min")
            print(f"切深: {r.get('cut_depth', 0):.2f} mm")
            print(f"切宽: {r.get('cut_width', 0):.2f} mm")
            print()
            print(f"线速度: {r.get('cutting_speed', 0):.2f} m/min")
            print(f"每齿进给: {r.get('feed_per_tooth', 0):.4f} mm")
            print()
            print(f"功率: {r.get('power', 0):.2f} kW")
            print(f"扭矩: {r.get('torque', 0):.2f} Nm")
            print(f"进给力: {r.get('feed_force', 0):.2f} N")
            print()
            print(f"底面粗糙度: {r.get('bottom_roughness', 0):.2f} μm")
            print(f"侧面粗糙度: {r.get('side_roughness', 0):.2f} μm")
            print(f"刀具寿命: {r.get('tool_life', 0):.2f} min")
            print()
            print(f"材料去除率: {r.get('material_removal_rate', 0):.2f} cm³/min")
            print(f"适应度: {r.get('fitness', 0):.6f}")
            print()
            print("=" * 80)
            print("约束检查:")
            print("=" * 80)
            
            # 检查约束
            power = r.get('power', 0)
            torque = r.get('torque', 0)
            cut_depth = r.get('cut_depth', 0)
            cut_width = r.get('cut_width', 0)
            
            # 约束值（从数据库查询）
            max_power = 5.5  # kW
            max_torque = 20  # Nm
            max_cut_depth = 10  # mm (刀具直径)
            max_cut_width = 10  # mm (刀具直径)
            
            power_ratio = power / max_power * 100
            torque_ratio = torque / max_torque * 100
            cut_depth_ratio = cut_depth / max_cut_depth * 100
            cut_width_ratio = cut_width / max_cut_width * 100
            
            print(f"功率使用率: {power_ratio:.1f}% (最大 {max_power} kW)")
            if power > max_power:
                print(f"  ❌ 超出约束！")
            else:
                print(f"  ✅ 满足约束")
            
            print(f"扭矩使用率: {torque_ratio:.1f}% (最大 {max_torque} Nm)")
            if torque > max_torque:
                print(f"  ❌ 超出约束！")
            else:
                print(f"  ✅ 满足约束")
            
            print(f"切深使用率: {cut_depth_ratio:.1f}% (最大 {max_cut_depth} mm)")
            if cut_depth > max_cut_depth:
                print(f"  ❌ 超出约束！")
            else:
                print(f"  ✅ 满足约束")
            
            print(f"切宽使用率: {cut_width_ratio:.1f}% (最大 {max_cut_width} mm)")
            if cut_width > max_cut_width:
                print(f"  ❌ 超出约束！")
            else:
                print(f"  ✅ 满足约束")
            
            print()
            print("=" * 80)
            
            # 检查是否有约束违规
            if (power > max_power or torque > max_torque or 
                cut_depth > max_cut_depth or cut_width > max_cut_width):
                print("⚠️  警告：优化结果超出约束限制！")
            else:
                print("✅ 所有约束均满足！")
    else:
        print(f"优化失败: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"请求失败: {str(e)}")
    import traceback
    traceback.print_exc()