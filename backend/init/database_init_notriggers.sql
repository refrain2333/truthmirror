-- =====================================================
-- 真相之镜数据库初始化脚本 - 无触发器版本
-- 数据库: MySQL 8.0+
-- 编码: UTF-8
-- =====================================================

-- 删除数据库（如果存在）并重新创建
DROP DATABASE IF EXISTS `truthmirror`;
CREATE DATABASE `truthmirror` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `truthmirror`;

-- =====================================================
-- 1. 用户表 (users) - 简化版本，约15个字段
-- =====================================================
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `email` VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱地址',
    `password` VARCHAR(255) NOT NULL COMMENT '密码（明文存储）',
    `role` VARCHAR(20) DEFAULT 'user' COMMENT '用户角色: user/admin',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    
    -- 基本信息
    `nickname` VARCHAR(100) DEFAULT NULL COMMENT '昵称',
    `bio` TEXT DEFAULT NULL COMMENT '个人简介',
    `location` VARCHAR(100) DEFAULT NULL COMMENT '所在地区',
    `birth_date` DATE DEFAULT NULL COMMENT '出生日期',
    
    -- 简化统计信息（3个）
    `events_created` INT DEFAULT 0 COMMENT '创建事件数',
    `votes_cast` INT DEFAULT 0 COMMENT '投票次数',
    `interests_marked` INT DEFAULT 0 COMMENT '表示兴趣次数',
    
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `last_login_at` TIMESTAMP DEFAULT NULL COMMENT '最后登录时间',
    
    INDEX `idx_username` (`username`),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- =====================================================
-- 2. 事件表 (events) - 简化AI分析
-- =====================================================
CREATE TABLE `events` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL COMMENT '事件标题',
    `description` TEXT NOT NULL COMMENT '事件描述',
    `keywords` VARCHAR(500) NOT NULL COMMENT '关键词',
    
    -- 状态流程: pending -> nominated -> processing -> voting -> confirmed
    `status` ENUM('pending', 'nominated', 'processing', 'voting', 'confirmed') DEFAULT 'pending' COMMENT '事件状态',
    
    -- 统计信息
    `interest_count` INT DEFAULT 0 COMMENT '感兴趣用户数',
    `vote_count` INT DEFAULT 0 COMMENT '总投票数',
    `support_votes` INT DEFAULT 0 COMMENT '支持票数',
    `oppose_votes` INT DEFAULT 0 COMMENT '反对票数',
    
    -- AI分析结果（简化）
    `ai_summary` TEXT DEFAULT NULL COMMENT 'AI分析总结',
    `ai_rating` ENUM('reliable', 'questionable', 'unreliable', 'insufficient') DEFAULT NULL COMMENT 'AI评价结果',
    
    -- 时间信息
    `nomination_deadline` TIMESTAMP DEFAULT NULL COMMENT '提名截止时间',
    `creator_id` INT NOT NULL COMMENT '创建者ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (`creator_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_title` (`title`),
    INDEX `idx_status` (`status`),
    INDEX `idx_creator_id` (`creator_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='事件表';

-- =====================================================
-- 3. 事件感兴趣表 (event_interests)
-- =====================================================
CREATE TABLE `event_interests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_id` INT NOT NULL COMMENT '事件ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '表示兴趣时间',
    
    FOREIGN KEY (`event_id`) REFERENCES `events`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_event_user` (`event_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='事件感兴趣表';

-- =====================================================
-- 4. 事件信息来源表 (information_sources) - 简化
-- =====================================================
CREATE TABLE `information_sources` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_id` INT NOT NULL COMMENT '事件ID',
    `url` VARCHAR(1000) NOT NULL COMMENT '信息来源URL',
    `title` VARCHAR(300) DEFAULT NULL COMMENT '来源标题',
    `website_name` VARCHAR(100) DEFAULT NULL COMMENT '网站名称',
    `content` TEXT DEFAULT NULL COMMENT '原始内容',
    `ai_summary` TEXT DEFAULT NULL COMMENT 'AI总结',
    `relevance_score` DECIMAL(5,2) DEFAULT 0.00 COMMENT '相关度分数',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (`event_id`) REFERENCES `events`(`id`) ON DELETE CASCADE,
    INDEX `idx_event_id` (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='事件信息来源表';

-- =====================================================
-- 5. 用户投票表 (votes) - 包含投票评价
-- =====================================================
CREATE TABLE `votes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_id` INT NOT NULL COMMENT '事件ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `stance` ENUM('support', 'oppose') NOT NULL COMMENT '投票立场',
    `ai_good_points` TEXT DEFAULT NULL COMMENT 'AI分析优点评价',
    `ai_bad_points` TEXT DEFAULT NULL COMMENT 'AI分析缺点评价',
    `user_comment` TEXT DEFAULT NULL COMMENT '用户投票理由',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '投票时间',
    
    FOREIGN KEY (`event_id`) REFERENCES `events`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_event_user` (`event_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户投票表';

-- =====================================================
-- 插入初始数据
-- =====================================================

-- 创建默认用户
INSERT INTO `users` (`username`, `email`, `password`, `role`, `nickname`) VALUES 
('admin', 'admin@truthmirror.com', 'admin123', 'admin', '系统管理员'),
('testuser', 'user@example.com', 'user123', 'user', '测试用户');

-- 创建示例事件
INSERT INTO `events` (`title`, `description`, `keywords`, `creator_id`, `nomination_deadline`) VALUES 
('测试事件', '这是一个测试事件，用于验证系统功能', '测试,功能', 1, DATE_ADD(NOW(), INTERVAL 7 DAY));

SELECT '数据库初始化完成' as message;