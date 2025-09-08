-- =====================================================
-- 真相之镜 (Truth Mirror) 数据库初始化脚本
-- 数据库: MySQL 8.0+
-- 编码: UTF-8
-- =====================================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `truthmirror` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `truthmirror`;

-- =====================================================
-- 1. 用户表 (users)
-- =====================================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `email` VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱地址',
    `password` VARCHAR(255) NOT NULL COMMENT '密码（明文存储）',
    `role` ENUM('user', 'admin') DEFAULT 'user' COMMENT '用户角色',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX `idx_username` (`username`),
    INDEX `idx_email` (`email`),
    INDEX `idx_role` (`role`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- =====================================================
-- 2. 事件表 (events)
-- =====================================================
CREATE TABLE IF NOT EXISTS `events` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL COMMENT '事件标题',
    `description` TEXT NOT NULL COMMENT '事件描述',
    `keywords` VARCHAR(500) NOT NULL COMMENT '关键词，逗号分隔',
    `status` ENUM('pending', 'nominated', 'processing', 'voting', 'confirmed') DEFAULT 'pending' COMMENT '事件状态',
    `interest_count` INT DEFAULT 0 COMMENT '兴趣度计数',
    `creator_id` INT NOT NULL COMMENT '创建者ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (`creator_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_title` (`title`),
    INDEX `idx_status` (`status`),
    INDEX `idx_creator_id` (`creator_id`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_interest_count` (`interest_count`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='事件表';

-- =====================================================
-- 3. 信息源表 (information_sources)
-- =====================================================
CREATE TABLE IF NOT EXISTS `information_sources` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_id` INT NOT NULL COMMENT '关联事件ID',
    `url` VARCHAR(1000) NOT NULL COMMENT '信息源链接',
    `title` VARCHAR(300) COMMENT '信息源标题',
    `content` LONGTEXT COMMENT '提取的内容',
    `stance` ENUM('support', 'oppose', 'neutral') COMMENT '立场：支持/反对/中性',
    `relevance_score` DECIMAL(5,4) DEFAULT 0.0000 COMMENT '相关性评分(0-1)',
    `ai_summary` TEXT COMMENT 'AI生成的摘要',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (`event_id`) REFERENCES `events`(`id`) ON DELETE CASCADE,
    INDEX `idx_event_id` (`event_id`),
    INDEX `idx_stance` (`stance`),
    INDEX `idx_relevance_score` (`relevance_score`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='信息源表';

-- =====================================================
-- 4. 投票表 (votes)
-- =====================================================
CREATE TABLE IF NOT EXISTS `votes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_id` INT NOT NULL COMMENT '关联事件ID',
    `user_id` INT NOT NULL COMMENT '投票用户ID',
    `stance` ENUM('support', 'oppose') NOT NULL COMMENT '投票立场：支持/反对',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '投票时间',
    
    FOREIGN KEY (`event_id`) REFERENCES `events`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_event_user` (`event_id`, `user_id`) COMMENT '一个用户对一个事件只能投一票',
    INDEX `idx_event_id` (`event_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_stance` (`stance`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='投票表';

-- =====================================================
-- 5. AI分析表 (ai_analyses)
-- =====================================================
CREATE TABLE IF NOT EXISTS `ai_analyses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_id` INT NOT NULL COMMENT '关联事件ID',
    `support_arguments` LONGTEXT COMMENT '正方论据',
    `oppose_arguments` LONGTEXT COMMENT '反方论据',
    `ai_judgment` ENUM('support', 'oppose') COMMENT 'AI初步判断',
    `confidence_score` DECIMAL(5,4) DEFAULT 0.0000 COMMENT 'AI置信度(0-1)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '分析时间',
    
    FOREIGN KEY (`event_id`) REFERENCES `events`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_event_analysis` (`event_id`) COMMENT '一个事件只有一个AI分析结果',
    INDEX `idx_ai_judgment` (`ai_judgment`),
    INDEX `idx_confidence_score` (`confidence_score`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI分析表';

-- =====================================================
-- 6. 事件详情表 (event_details) - AI整合后的完整阐述
-- =====================================================
CREATE TABLE IF NOT EXISTS `event_details` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_id` INT NOT NULL COMMENT '关联事件ID',
    `background_summary` LONGTEXT COMMENT '事件背景摘要',
    `key_players` TEXT COMMENT '关键人物/机构',
    `timeline` LONGTEXT COMMENT '事件时间线',
    `core_facts` LONGTEXT COMMENT '核心事实',
    `controversy_points` LONGTEXT COMMENT '争议焦点',
    `evidence_summary` LONGTEXT COMMENT '证据汇总',
    `social_impact` TEXT COMMENT '社会影响',
    `expert_opinions` LONGTEXT COMMENT '专家观点汇总',
    `media_coverage` LONGTEXT COMMENT '媒体报道汇总',
    `final_conclusion` LONGTEXT COMMENT 'AI最终结论',
    `reliability_score` DECIMAL(5,4) DEFAULT 0.0000 COMMENT '可靠性评分(0-1)',
    `completeness_score` DECIMAL(5,4) DEFAULT 0.0000 COMMENT '完整性评分(0-1)',
    `last_updated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (`event_id`) REFERENCES `events`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_event_detail` (`event_id`) COMMENT '一个事件只有一个详情记录',
    INDEX `idx_reliability_score` (`reliability_score`),
    INDEX `idx_completeness_score` (`completeness_score`),
    INDEX `idx_last_updated` (`last_updated`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='事件详情表-AI整合的完整阐述';

-- =====================================================
-- 7. 事件兴趣表 (event_interests)
-- =====================================================
CREATE TABLE IF NOT EXISTS `event_interests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_id` INT NOT NULL COMMENT '关联事件ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '表示兴趣时间',
    
    FOREIGN KEY (`event_id`) REFERENCES `events`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_event_user_interest` (`event_id`, `user_id`) COMMENT '一个用户对一个事件只能表示一次兴趣',
    INDEX `idx_event_id` (`event_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='事件兴趣表';

-- =====================================================
-- 8. 系统日志表 (system_logs) - 可选
-- =====================================================
CREATE TABLE IF NOT EXISTS `system_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_id` INT COMMENT '相关事件ID',
    `user_id` INT COMMENT '相关用户ID',
    `action` VARCHAR(50) NOT NULL COMMENT '操作类型',
    `description` TEXT COMMENT '操作描述',
    `ip_address` VARCHAR(45) COMMENT 'IP地址',
    `user_agent` VARCHAR(500) COMMENT '用户代理',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    
    INDEX `idx_event_id` (`event_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_action` (`action`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';

-- =====================================================
-- 创建视图：事件统计信息
-- =====================================================
CREATE OR REPLACE VIEW `v_event_stats` AS
SELECT 
    e.`id` AS `event_id`,
    e.`title`,
    e.`status`,
    e.`interest_count`,
    e.`created_at`,
    COALESCE(v.`total_votes`, 0) AS `total_votes`,
    COALESCE(v.`support_votes`, 0) AS `support_votes`,
    COALESCE(v.`oppose_votes`, 0) AS `oppose_votes`,
    CASE 
        WHEN COALESCE(v.`total_votes`, 0) > 0 
        THEN ROUND(COALESCE(v.`support_votes`, 0) * 100.0 / v.`total_votes`, 2)
        ELSE 0 
    END AS `support_percentage`,
    CASE 
        WHEN COALESCE(v.`total_votes`, 0) > 0 
        THEN ROUND(COALESCE(v.`oppose_votes`, 0) * 100.0 / v.`total_votes`, 2)
        ELSE 0 
    END AS `oppose_percentage`,
    COALESCE(s.`source_count`, 0) AS `source_count`,
    a.`ai_judgment`,
    a.`confidence_score`,
    d.`reliability_score`,
    d.`completeness_score`,
    d.`last_updated` AS `detail_last_updated`
FROM `events` e
LEFT JOIN (
    SELECT 
        `event_id`,
        COUNT(*) AS `total_votes`,
        SUM(CASE WHEN `stance` = 'support' THEN 1 ELSE 0 END) AS `support_votes`,
        SUM(CASE WHEN `stance` = 'oppose' THEN 1 ELSE 0 END) AS `oppose_votes`
    FROM `votes`
    GROUP BY `event_id`
) v ON e.`id` = v.`event_id`
LEFT JOIN (
    SELECT 
        `event_id`,
        COUNT(*) AS `source_count`
    FROM `information_sources`
    GROUP BY `event_id`
) s ON e.`id` = s.`event_id`
LEFT JOIN `ai_analyses` a ON e.`id` = a.`event_id`
LEFT JOIN `event_details` d ON e.`id` = d.`event_id`;

-- =====================================================
-- 数据库初始化完成
-- =====================================================
SELECT 'Truth Mirror Database initialized successfully!' AS message;