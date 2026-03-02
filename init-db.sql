-- 初始化数据库

-- 知识条目表
CREATE TABLE IF NOT EXISTS knowledge_items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    source VARCHAR(255),
    source_url VARCHAR(1000),
    embedding_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 学习任务表
CREATE TABLE IF NOT EXISTS learning_tasks (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    keyword VARCHAR(255) NOT NULL,
    video_id VARCHAR(255),
    video_url VARCHAR(1000),
    video_title VARCHAR(500),
    video_author VARCHAR(255),
    video_duration INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    extracted_text TEXT,
    knowledge_extracted BOOLEAN DEFAULT FALSE,
    celery_task_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 学习关键词表
CREATE TABLE IF NOT EXISTS learning_keywords (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    keyword VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, keyword)
);

-- 模型配置表
CREATE TABLE IF NOT EXISTS model_configs (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL UNIQUE,
    model_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255),
    api_base VARCHAR(255),
    is_active BOOLEAN DEFAULT FALSE,
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 对话历史表
CREATE TABLE IF NOT EXISTS conversation_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    user_input TEXT NOT NULL,
    analysis_result JSONB,
    model_used VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_items(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_items USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_learning_status ON learning_tasks(status);
CREATE INDEX IF NOT EXISTS idx_learning_platform ON learning_tasks(platform);
CREATE INDEX IF NOT EXISTS idx_learning_video_id ON learning_tasks(video_id);
CREATE INDEX IF NOT EXISTS idx_keywords_platform ON learning_keywords(platform);
CREATE INDEX IF NOT EXISTS idx_keywords_active ON learning_keywords(is_active);
CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_history(session_id);

-- 插入默认模型配置
INSERT INTO model_configs (provider, model_name, is_active) VALUES
    ('openai', 'gpt-4o', TRUE),
    ('qwen', 'qwen-max', FALSE),
    ('ollama', 'qwen2.5:7b', FALSE)
ON CONFLICT (provider) DO NOTHING;

-- 插入默认学习关键词
INSERT INTO learning_keywords (platform, keyword) VALUES
    ('bilibili', '职场话术'),
    ('bilibili', '领导意图'),
    ('bilibili', '官场智慧'),
    ('bilibili', '人情世故'),
    ('bilibili', '社交技巧'),
    ('bilibili', '职场沟通'),
    ('bilibili', '心理学'),
    ('bilibili', '人际关系'),
    ('bilibili', '情商提升')
ON CONFLICT (platform, keyword) DO NOTHING;
