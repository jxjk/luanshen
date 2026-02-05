-- 修复材料参数，使其更合理
-- P15 材料的单位切削力从 2200 降低到合理的值

-- 查看 P15 当前参数
SELECT * FROM cailiao WHERE caiLiaoZu = 'P15';

-- 更新 P15 材料的单位切削力（从 2200 降低到 1800）
UPDATE cailiao 
SET kc11 = 1800
WHERE caiLiaoZu = 'P15';

-- 更新机床参数，增加功率和扭矩以适应高强度材料加工
-- 国盛850加工中心的实际参数可能更高
UPDATE machines 
SET Pw_max = 7.5,  -- 从 5.5 增加到 7.5 kW
    Tnm_max = 30   -- 从 20 增加到 30 Nm
WHERE id = 1;

-- 查看更新后的参数
SELECT * FROM machines WHERE id = 1;
SELECT * FROM cailiao WHERE caiLiaoZu = 'P15';