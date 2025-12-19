-- Initial Database Setup for Behflow
-- This script creates all necessary tables, enums, and indexes
-- Run this script first to initialize the database

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

-- Task-related enums
CREATE TYPE priority_enum AS ENUM ('low', 'medium', 'high');
CREATE TYPE status_enum AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');

-- Automated process enums
CREATE TYPE trigger_type_enum AS ENUM ('manual', 'time_based', 'event_based');
CREATE TYPE process_status_enum AS ENUM ('pending', 'running', 'completed', 'failed', 'disabled');

-- ============================================================================
-- TABLES
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date_gregorian TIMESTAMP WITH TIME ZONE,
    date_added_gregorian TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    due_date_jalali VARCHAR(50),
    date_added_jalali VARCHAR(50) NOT NULL,
    priority priority_enum NOT NULL DEFAULT 'medium',
    status status_enum NOT NULL DEFAULT 'pending',
    tags TEXT[],
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for tasks
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date_gregorian);

-- Chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create indexes for chat sessions
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_is_active ON chat_sessions(is_active);

-- Chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tokens_used INTEGER
);

-- Create indexes for chat messages
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- Automated processes table
CREATE TABLE IF NOT EXISTS automated_processes (
    process_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    trigger_type trigger_type_enum NOT NULL,
    schedule_config JSONB,
    process_config JSONB,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_executed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for automated processes
CREATE INDEX IF NOT EXISTS idx_automated_processes_name ON automated_processes(name);
CREATE INDEX IF NOT EXISTS idx_automated_processes_trigger_type ON automated_processes(trigger_type);
CREATE INDEX IF NOT EXISTS idx_automated_processes_is_enabled ON automated_processes(is_enabled);

-- Automated process executions table
CREATE TABLE IF NOT EXISTS automated_process_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES automated_processes(process_id) ON DELETE CASCADE,
    status process_status_enum NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    result JSONB,
    error_message TEXT
);

-- Create indexes for automated process executions
CREATE INDEX IF NOT EXISTS idx_automated_process_executions_process_id ON automated_process_executions(process_id);
CREATE INDEX IF NOT EXISTS idx_automated_process_executions_started_at ON automated_process_executions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_automated_process_executions_status ON automated_process_executions(status);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for tasks table
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for chat_sessions table
CREATE TRIGGER update_chat_sessions_updated_at
    BEFORE UPDATE ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for automated_processes table
CREATE TRIGGER update_automated_processes_updated_at
    BEFORE UPDATE ON automated_processes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default automated processes
INSERT INTO automated_processes (
    name,
    description,
    trigger_type,
    schedule_config,
    process_config,
    is_enabled
) VALUES (
    'reschedule_remaining_tasks',
    'Reschedules incomplete tasks from previous days to the current day',
    'time_based',
    '{"hour": 7, "minute": 30, "timezone": "Asia/Tehran"}'::jsonb,
    '{"include_statuses": ["pending", "in_progress"], "update_to_today": true}'::jsonb,
    TRUE
) ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- List all created tables
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- List all created types
SELECT n.nspname as schema, t.typname as type_name
FROM pg_type t 
LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace 
WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid)) 
AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_type el WHERE el.oid = t.typelem AND el.typarray = t.oid)
AND n.nspname = 'public'
ORDER BY type_name;

-- Confirm automated processes
SELECT process_id, name, trigger_type, is_enabled 
FROM automated_processes;

