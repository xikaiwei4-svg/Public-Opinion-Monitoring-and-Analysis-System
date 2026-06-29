-- ============================================================
-- init_db.sql — 校园舆情系统 数据库初始化脚本
-- 从 ORM 模型手动翻译为纯 SQL 建表语句
-- ============================================================
-- 用法:
--   mysql -u root -p < init_db.sql
-- 或在 MySQL 中执行:
--   source /path/to/init_db.sql;
-- ============================================================

-- 创建数据库（若不存在）
CREATE DATABASE IF NOT EXISTS `campus_opinion`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `campus_opinion`;

-- ============================================================
-- 1. users — 用户表
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
    `id`            INT           NOT NULL AUTO_INCREMENT,
    `username`      VARCHAR(100)  NOT NULL,
    `email`         VARCHAR(200)  DEFAULT NULL,
    `password_hash` VARCHAR(255)  NOT NULL,
    `role`          VARCHAR(50)   DEFAULT 'user',
    `is_active`     TINYINT(1)    DEFAULT 1,
    `created_at`    DATETIME      DEFAULT CURRENT_TIMESTAMP,
    `last_login`    DATETIME      DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 2. opinions — 舆情记录表
-- ============================================================
CREATE TABLE IF NOT EXISTS `opinions` (
    `id`               INT           NOT NULL AUTO_INCREMENT,
    `title`            VARCHAR(500)  DEFAULT NULL,
    `content`          TEXT          DEFAULT NULL,
    `source_platform`  VARCHAR(50)   DEFAULT NULL,
    `source_url`       VARCHAR(1000) DEFAULT NULL,
    `author`           VARCHAR(200)  DEFAULT NULL,
    `author_id`        VARCHAR(200)  DEFAULT NULL,
    `publish_time`     DATETIME      DEFAULT NULL,
    `crawl_time`       DATETIME      DEFAULT NULL,
    `sentiment`        VARCHAR(20)   DEFAULT NULL,
    `sentiment_score`  FLOAT         DEFAULT NULL,
    `keywords`         VARCHAR(500)  DEFAULT NULL,
    `read_count`       INT           DEFAULT 0,
    `like_count`       INT           DEFAULT 0,
    `comment_count`    INT           DEFAULT 0,
    `share_count`      INT           DEFAULT 0,
    `is_hot`           TINYINT(1)    DEFAULT 0,
    `hot_score`        FLOAT         DEFAULT 0.0,
    PRIMARY KEY (`id`),
    INDEX `idx_publish_time` (`publish_time`),
    INDEX `idx_sentiment` (`sentiment`),
    INDEX `idx_source_platform` (`source_platform`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 3. hot_topics — 热点话题表
-- ============================================================
CREATE TABLE IF NOT EXISTS `hot_topics` (
    `id`                     INT           NOT NULL AUTO_INCREMENT,
    `topic`                  VARCHAR(500)  NOT NULL,
    `keyword`                VARCHAR(200)  DEFAULT NULL,
    `mention_count`          INT           DEFAULT 0,
    `sentiment_distribution` VARCHAR(500)  DEFAULT NULL,
    `trend`                  VARCHAR(50)   DEFAULT NULL,
    `first_seen`             DATETIME      DEFAULT NULL,
    `last_seen`              DATETIME      DEFAULT NULL,
    `related_opinions`       VARCHAR(1000) DEFAULT NULL,
    PRIMARY KEY (`id`),
    INDEX `idx_topic` (`topic`(255)),
    INDEX `idx_keyword` (`keyword`),
    INDEX `idx_first_seen` (`first_seen`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 4. trend_data — 趋势数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS `trend_data` (
    `id`              INT           NOT NULL AUTO_INCREMENT,
    `date`            DATETIME      NOT NULL,
    `platform`        VARCHAR(50)   DEFAULT NULL,
    `total_count`     INT           DEFAULT 0,
    `positive_count`  INT           DEFAULT 0,
    `negative_count`  INT           DEFAULT 0,
    `neutral_count`   INT           DEFAULT 0,
    `hot_topics`      VARCHAR(1000) DEFAULT NULL,
    PRIMARY KEY (`id`),
    INDEX `idx_date_platform` (`date`, `platform`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 5. crawler_logs — 爬虫日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS `crawler_logs` (
    `id`             INT           NOT NULL AUTO_INCREMENT,
    `task_id`        VARCHAR(100)  DEFAULT NULL,
    `platform`       VARCHAR(50)   NOT NULL,
    `status`         VARCHAR(50)   DEFAULT NULL,
    `start_time`     DATETIME      DEFAULT NULL,
    `end_time`       DATETIME      DEFAULT NULL,
    `total_count`    INT           DEFAULT 0,
    `success_count`  INT           DEFAULT 0,
    `error_count`    INT           DEFAULT 0,
    `error_message`  TEXT          DEFAULT NULL,
    PRIMARY KEY (`id`),
    INDEX `idx_task_id` (`task_id`),
    INDEX `idx_platform` (`platform`),
    INDEX `idx_start_time` (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 6. alert_records — 告警记录表
-- ============================================================
CREATE TABLE IF NOT EXISTS `alert_records` (
    `id`                INT           NOT NULL AUTO_INCREMENT,
    `alert_type`        VARCHAR(50)   NOT NULL,
    `alert_level`       VARCHAR(20)   DEFAULT NULL,
    `title`             VARCHAR(500)  NOT NULL,
    `description`       TEXT          DEFAULT NULL,
    `opinion_id`        INT           DEFAULT NULL,
    `hot_topic_id`      INT           DEFAULT NULL,
    `trigger_condition` VARCHAR(500)  DEFAULT NULL,
    `created_at`        DATETIME      DEFAULT CURRENT_TIMESTAMP,
    `processed`         TINYINT(1)    DEFAULT 0,
    `processed_at`      DATETIME      DEFAULT NULL,
    `processed_by`      INT           DEFAULT NULL,
    `processing_note`   TEXT          DEFAULT NULL,
    PRIMARY KEY (`id`),
    INDEX `idx_alert_type` (`alert_type`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_processed` (`processed`),
    CONSTRAINT `fk_alert_opinion` FOREIGN KEY (`opinion_id`) REFERENCES `opinions` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_alert_hot_topic` FOREIGN KEY (`hot_topic_id`) REFERENCES `hot_topics` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 建表完成确认
-- ============================================================
SELECT '✅ 建表完成' AS `status`,
       CONCAT('数据库: ', DATABASE()) AS `database`,
       (SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE()) AS `table_count`;
