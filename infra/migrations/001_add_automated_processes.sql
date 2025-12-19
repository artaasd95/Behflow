-- Migration: Add Automated Processes Tables (LEGACY)
-- This script is now included in 000_init_database.sql
-- Keeping for reference only - will not execute if types/tables already exist

-- Create enum types for automated processes (skip if already exist)
DO $$ BEGIN
    CREATE TYPE trigger_type_enum AS ENUM ('manual', 'time_based', 'event_based');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE process_status_enum AS ENUM ('pending', 'running', 'completed', 'failed', 'disabled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create automated_processes table
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

-- Create index on name for faster lookups
CREATE INDEX IF NOT EXISTS idx_automated_processes_name ON automated_processes(name);

-- Create index on trigger_type for filtering
CREATE INDEX IF NOT EXISTS idx_automated_processes_trigger_type ON automated_processes(trigger_type);

-- Create automated_process_executions table
CREATE TABLE IF NOT EXISTS automated_process_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES automated_processes(process_id) ON DELETE CASCADE,
    status process_status_enum NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    result JSONB,
    error_message TEXT
);

-- Create index on process_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_automated_process_executions_process_id ON automated_process_executions(process_id);

-- Create index on started_at for sorting execution history
CREATE INDEX IF NOT EXISTS idx_automated_process_executions_started_at ON automated_process_executions(started_at DESC);

-- Create trigger to automatically update updated_at timestamp (skip if already exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop trigger if exists and recreate (to ensure compatibility)
DROP TRIGGER IF EXISTS update_automated_processes_updated_at ON automated_processes;
CREATE TRIGGER update_automated_processes_updated_at
    BEFORE UPDATE ON automated_processes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default reschedule remaining tasks process
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

-- Verify the setup
SELECT 
    process_id, 
    name, 
    trigger_type, 
    schedule_config, 
    is_enabled 
FROM automated_processes;
