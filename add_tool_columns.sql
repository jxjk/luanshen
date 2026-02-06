-- 为 tools 表添加缺失的列
ALTER TABLE tools ADD COLUMN elastic_modulus FLOAT NULL COMMENT '弹性模量 MPa';
ALTER TABLE tools ADD COLUMN overhang_length FLOAT NULL COMMENT '悬伸长度 mm';