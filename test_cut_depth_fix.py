"""
测试切深修复 - 验证刀具挠度约束优化后的效果
"""
import requests
import json

# 测试数据 - 使用刀具2（Φ35mm牛鼻刀）
test_data = {
    "material_id": "P15",
    "tool_id": "2",
    "machine_id": "1",
    "strategy_id": "1",
    "population_size": 2048,  # 增加种群大小以获得更好的优化结果
    "generations": 100
}

print("=" * 80)
print("测试切深修复 - 验证刀具挠度约束优化")
print("=" * 80)
print(f"测试数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
print()

# 调用优化 API
try:
    print("正在调用优化 API...")
    response = requests.post(
        "http://localhost:5007/api/v1/optimization/optimize",
        json=test_data,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ 优化成功！")
        print()
        print("优化结果:")
        print("=" * 80)
        
        if result.get("result"):
            r = result["result"]
            speed = r.get('speed', 0)
            feed = r.get('feed', 0)
            cut_depth = r.get('cut_depth', 0)
            cut_width = r.get('cut_width', 0)
            
            print(f"转速: {speed:.2f} r/min")
            print(f"进给: {feed:.2f} mm/min")
            print(f"切深: {cut_depth:.2f} mm ⭐ 关注此项")
            print(f"切宽: {cut_width:.2f} mm")
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
            
            # 约束值（从数据库查询）
            max_power = 5.5  # kW
            max_torque = 20  # Nm
            max_cut_depth = 10  # mm (刀具直径)
            max_cut_width = 10  # mm (刀具直径)
            
            power_ratio = r.get('power', 0) / max_power * 100
            torque_ratio = r.get('torque', 0) / max_torque * 100
            cut_depth_ratio = cut_depth / max_cut_depth * 100
            cut_width_ratio = cut_width / max_cut_width * 100
            
            print(f"功率使用率: {power_ratio:.1f}% (最大 {max_power} kW)")
            print(f"扭矩使用率: {torque_ratio:.1f}% (最大 {max_torque} Nm)")
            print(f"切深使用率: {cut_depth_ratio:.1f}% (最大 {max_cut_depth} mm)")
            print(f"切宽使用率: {cut_width_ratio:.1f}% (最大 {max_cut_width} mm)")
            print()
            
            # 计算刀具挠度（手动验证）
            tool_diameter = 35.0  # 刀具2的直径
            tool_overhang = 60.0  # 悬伸长度
            tool_elastic_modulus = 630000.0  # 弹性模量 (MPa)
            max_deflection = 0.15 * tool_diameter  # 最大允许挠度
            
            # 截面惯性矩
            moment_of_inertia = 3.14159 * (tool_diameter ** 4) / 64.0
            # 挠度计算
            tool_deflection = (r.get('feed_force', 0) * (tool_overhang ** 3)) / (3.0 * tool_elastic_modulus * moment_of_inertia)
            
            print(f"刀具挠度计算:")
            print(f"  刀具直径: {tool_diameter} mm")
            print(f"  悬伸长度: {tool_overhang} mm")
            print(f"  弹性模量: {tool_elastic_modulus} MPa")
            print(f"  截面惯性矩: {moment_of_inertia:.2f} mm⁴")
            print(f"  进给力: {r.get('feed_force', 0):.2f} N")
            print(f"  计算挠度: {tool_deflection:.4f} mm")
            print(f"  最大允许挠度: {max_deflection:.3f} mm")
            print(f"  挠度使用率: {tool_deflection / max_deflection * 100:.1f}%")
            print()
            
            print("=" * 80)
            print("效果评估:")
            print("=" * 80)
            
            # 评估切深是否合理
            if cut_depth >= 2.0:
                print("✅ 切深修复成功！切深 >= 2.0mm，满足粗加工要求")
            elif cut_depth >= 1.5:
                print("⚠️  切深有所改善，但仍偏低（1.5-2.0mm）")
            else:
                print("❌ 切深仍然过低（< 1.5mm），需要进一步优化")
            
            # 评估挠度是否合理
            if tool_deflection <= max_deflection:
                print("✅ 刀具挠度在允许范围内")
            else:
                print(f"❌ 刀具挠度超出限制（{tool_deflection:.4f} > {max_deflection:.3f} mm）")
            
            print()
            
            # 建议
            print("优化建议:")
            if cut_depth < 2.0:
                print("- 可以尝试增加种群大小和迭代次数")
                print("- 检查刀具的 ap_max 参数是否设置合理")
                print("- 考虑调整刀具挠度约束的惩罚权重")
            else:
                print("- 当前切深已经合理，可以用于实际加工")
                print("- 建议在实际加工中监控刀具磨损情况")
            
    else:
        print(f"❌ 优化失败: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ 请求失败: {str(e)}")
    import traceback
    traceback.print_exc()
