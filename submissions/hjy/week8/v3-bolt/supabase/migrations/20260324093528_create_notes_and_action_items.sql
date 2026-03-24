/*
  # Create Notes and Action Items Tables

  1. New Tables
    - `notes`
      - `id` (uuid, primary key)
      - `title` (text, required)
      - `content` (text, required)
      - `created_at` (timestamp with timezone, defaults to now)
    
    - `action_items`
      - `id` (uuid, primary key)
      - `description` (text, required)
      - `completed` (boolean, defaults to false)
      - `created_at` (timestamp with timezone, defaults to now)
  
  2. Security
    - Enable RLS on both tables
    - Add policies for public access (for single-user app without authentication)
    - Policies allow all operations (SELECT, INSERT, UPDATE, DELETE)
*/

CREATE TABLE IF NOT EXISTS notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  content text NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS action_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  description text NOT NULL,
  completed boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations on notes"
  ON notes
  FOR ALL
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow all operations on action_items"
  ON action_items
  FOR ALL
  USING (true)
  WITH CHECK (true);