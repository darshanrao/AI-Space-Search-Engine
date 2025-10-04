-- Supabase Database Setup for Space Bio Chatbot
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create threads table
CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    title TEXT,
    context JSONB DEFAULT '{}'::jsonb NOT NULL
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    thread_id TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    meta JSONB DEFAULT '{}'::jsonb NOT NULL
);

-- Create index for efficient message queries
CREATE INDEX IF NOT EXISTS idx_messages_thread_id_created_at 
ON messages(thread_id, created_at);

-- Create index for thread queries
CREATE INDEX IF NOT EXISTS idx_threads_created_at 
ON threads(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_threads_updated_at 
    BEFORE UPDATE ON threads 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data (optional)
INSERT INTO threads (id, title, context) VALUES 
('sample-thread-1', 'Space Biology Discussion', '{"organism": "human", "conditions": ["microgravity"]}'),
('sample-thread-2', 'Research Questions', '{"topic": "space_medicine", "focus": "radiation"}')
ON CONFLICT (id) DO NOTHING;

INSERT INTO messages (thread_id, role, content, meta) VALUES 
('sample-thread-1', 'user', 'What is space biology?', '{}'),
('sample-thread-1', 'assistant', 'Space biology is the study of how living organisms are affected by and adapt to the unique environmental conditions of space.', '{}'),
('sample-thread-2', 'user', 'How does microgravity affect human physiology?', '{}'),
('sample-thread-2', 'assistant', 'Microgravity affects human physiology in several ways, including muscle atrophy, bone density loss, and fluid redistribution.', '{}')
ON CONFLICT (id) DO NOTHING;

-- Grant necessary permissions
GRANT ALL ON threads TO postgres;
GRANT ALL ON messages TO postgres;
GRANT USAGE ON SCHEMA public TO postgres;
