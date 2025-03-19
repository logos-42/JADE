-- 创建智能体表
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    did VARCHAR(255) NOT NULL,
    role JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建对话表
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    mode VARCHAR(50) NOT NULL DEFAULT 'interactive',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建消息表
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    sender VARCHAR(255) NOT NULL,
    receiver VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL DEFAULT 'text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建参与者表（多对多关系：对话-智能体）
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    agent_id INTEGER REFERENCES agents(id),
    role VARCHAR(50) DEFAULT 'participant',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_participants_conversation_id ON participants(conversation_id);
CREATE INDEX idx_participants_agent_id ON participants(agent_id);
CREATE INDEX idx_agents_did ON agents(did);

-- 创建两个测试智能体
INSERT INTO agents (id, name, did, role, created_at, updated_at) VALUES 
(0, '用户', 'did:efficode:user', '{"description": "代表系统用户的记录"}', NOW(), NOW()),
(1, '测试智能体1', 'did:efficode:test1', '{"description": "这是一个测试智能体"}', NOW(), NOW()),
(2, '测试智能体2', 'did:efficode:test2', '{"description": "这是另一个测试智能体"}', NOW(), NOW())
ON CONFLICT (id) DO NOTHING; 