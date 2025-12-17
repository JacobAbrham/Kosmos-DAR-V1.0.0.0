-- Database initialization script
-- Creates initial tables and data for KOSMOS

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS agents;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS mcp;

-- Set search path
SET search_path TO public, agents, audit, mcp;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Agent executions table
CREATE TABLE IF NOT EXISTS agents.executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES users(id),
    status VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit.logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- MCP server registry
CREATE TABLE IF NOT EXISTS mcp.servers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    endpoint VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    capabilities JSONB DEFAULT '[]'::jsonb,
    configuration JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_executions_agent_name ON agents.executions(agent_name);
CREATE INDEX idx_executions_user_id ON agents.executions(user_id);
CREATE INDEX idx_executions_status ON agents.executions(status);
CREATE INDEX idx_executions_started_at ON agents.executions(started_at);
CREATE INDEX idx_audit_user_id ON audit.logs(user_id);
CREATE INDEX idx_audit_action ON audit.logs(action);
CREATE INDEX idx_audit_created_at ON audit.logs(created_at);
CREATE INDEX idx_mcp_servers_name ON mcp.servers(name);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_servers_updated_at BEFORE UPDATE ON mcp.servers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password should be changed immediately)
INSERT INTO users (email, username, full_name, is_superuser)
VALUES ('admin@kosmos.local', 'admin', 'System Administrator', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO kosmos;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA agents TO kosmos;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO kosmos;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA mcp TO kosmos;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO kosmos;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA agents TO kosmos;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA audit TO kosmos;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA mcp TO kosmos;
