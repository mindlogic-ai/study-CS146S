export interface Note {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface ActionItem {
  id: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}
