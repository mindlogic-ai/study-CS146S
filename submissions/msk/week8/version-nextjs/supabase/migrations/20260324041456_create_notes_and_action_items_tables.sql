/*
  # Create notes and action_items tables

  1. New Tables
    - `notes` - Store note records with title and content
      - `id` (uuid, primary key)
      - `title` (text, required)
      - `content` (text, required)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    
    - `action_items` - Store action item records with completion status
      - `id` (uuid, primary key)
      - `description` (text, required)
      - `completed` (boolean, default false)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Security
    - Enable RLS on both tables
    - Add public read/write policies (for now, can be restricted later)
    - All records are accessible to anyone (public use case)
*/

CREATE TABLE IF NOT EXISTS notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  content text NOT NULL,
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

CREATE POLICY "notes_are_public"
  ON notes
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "notes_insert_public"
  ON notes
  FOR INSERT
  TO public
  WITH CHECK (true);

CREATE POLICY "notes_update_public"
  ON notes
  FOR UPDATE
  TO public
  USING (true)
  WITH CHECK (true);

CREATE POLICY "notes_delete_public"
  ON notes
  FOR DELETE
  TO public
  USING (true);

CREATE POLICY "action_items_are_public"
  ON action_items
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "action_items_insert_public"
  ON action_items
  FOR INSERT
  TO public
  WITH CHECK (true);

CREATE POLICY "action_items_update_public"
  ON action_items
  FOR UPDATE
  TO public
  USING (true)
  WITH CHECK (true);

CREATE POLICY "action_items_delete_public"
  ON action_items
  FOR DELETE
  TO public
  USING (true);

