/*
  # Notes & Action Items Schema

  1. New Tables
    - `notes`
      - `id` (uuid, primary key, auto-generated)
      - `title` (text, max 200 chars)
      - `content` (text)
      - `created_at` (timestamptz, auto-generated)
      - `updated_at` (timestamptz, auto-updated)
    
    - `action_items`
      - `id` (uuid, primary key, auto-generated)
      - `description` (text)
      - `completed` (boolean, default false)
      - `created_at` (timestamptz, auto-generated)
      - `updated_at` (timestamptz, auto-updated)

  2. Security
    - Enable RLS on both tables
    - Add policies for public access (for demo purposes)
    - Insert sample seed data

  3. Sample Data
    - 2 sample notes: "Welcome" and "Demo"
    - 2 sample action items: "Try pre-commit" and "Run tests"
*/

CREATE TABLE IF NOT EXISTS notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL CHECK (char_length(title) <= 200),
  content text NOT NULL DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS action_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  description text NOT NULL,
  completed boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to notes"
  ON notes FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert access to notes"
  ON notes FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update access to notes"
  ON notes FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public read access to action_items"
  ON action_items FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert access to action_items"
  ON action_items FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update access to action_items"
  ON action_items FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

INSERT INTO notes (title, content) VALUES
  ('Welcome', 'Welcome to your Notes & Action Items app! This is a productivity tool to help you organize your thoughts and tasks.'),
  ('Demo', 'This is a demo note showing how the app works. You can add, search, and update notes easily.')
ON CONFLICT DO NOTHING;

INSERT INTO action_items (description, completed) VALUES
  ('Try pre-commit', false),
  ('Run tests', false)
ON CONFLICT DO NOTHING;