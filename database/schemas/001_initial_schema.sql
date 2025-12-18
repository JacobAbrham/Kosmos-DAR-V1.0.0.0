-- Initial database schema for KOSMOS
-- Creates core tables for agents, conversations, and voting system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    agent_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    description TEXT,
    capabilities JSONB,
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id),
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pentarchy votes table
CREATE TABLE IF NOT EXISTS pentarchy_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proposal_id UUID NOT NULL,
    agent_id UUID REFERENCES agents(id),
    vote VARCHAR(10) NOT NULL, -- 'approve', 'reject', 'abstain'
    reasoning TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent executions table
CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id),
    task_type VARCHAR(100),
    status VARCHAR(20), -- 'pending', 'running', 'completed', 'failed'
    input JSONB,
    output JSONB,
    error TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_agent_id ON messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_pentarchy_votes_proposal_id ON pentarchy_votes(proposal_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_id ON agent_executions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status);

-- Insert default agents
INSERT INTO agents (name, agent_type, description, capabilities) VALUES
('Zeus', 'orchestrator', 'Central orchestrator and supervisor', '["orchestration", "supervision", "pentarchy_coordination"]'),
('Hermes', 'communications', 'Communications and routing agent', '["routing", "messaging", "notifications"]'),
('AEGIS', 'security', 'Security and compliance monitoring', '["security", "compliance", "kill_switch"]'),
('Chronos', 'scheduling', 'Scheduling and temporal operations', '["scheduling", "cron_jobs", "reminders"]'),
('Athena', 'knowledge', 'Knowledge management and RAG', '["knowledge_retrieval", "rag", "search"]'),
('Hephaestus', 'devops', 'DevOps and infrastructure operations', '["infrastructure", "deployment", "monitoring"]'),
('Nur PROMETHEUS', 'strategy', 'Analytics and strategic planning', '["analytics", "strategy", "pentarchy_voting"]'),
('Iris', 'interface', 'Communications and notifications', '["messaging", "notifications", "ui_updates"]'),
('MEMORIX', 'memory', 'Memory management and context', '["memory_storage", "context_management", "retrieval"]'),
('Hestia', 'personalization', 'Personalization and user experience', '["personalization", "preferences", "media"]'),
('Morpheus', 'learning', 'Learning and optimization', '["learning", "optimization", "model_training"]')
ON CONFLICT (name) DO NOTHING;

COMMENT ON TABLE agents IS 'Core agent definitions for the KOSMOS system';
COMMENT ON TABLE conversations IS 'User conversation sessions';
COMMENT ON TABLE messages IS 'Individual messages within conversations';
COMMENT ON TABLE pentarchy_votes IS 'Voting records for Pentarchy governance';
COMMENT ON TABLE agent_executions IS 'Agent task execution logs and metrics';
