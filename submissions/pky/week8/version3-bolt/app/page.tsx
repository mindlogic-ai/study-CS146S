'use client';

import { useState, useEffect, useCallback } from 'react';

interface Note {
  id: number;
  title: string;
  content: string;
  createdAt: string;
  updatedAt: string;
}

interface ActionItem {
  id: number;
  description: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

export default function Home() {
  // Notes state
  const [notes, setNotes] = useState<Note[]>([]);
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [noteSearch, setNoteSearch] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [editNoteTitle, setEditNoteTitle] = useState('');
  const [editNoteContent, setEditNoteContent] = useState('');

  // Action Items state
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [actionDesc, setActionDesc] = useState('');
  const [completedFilter, setCompletedFilter] = useState<string>('all');
  const [editingItemId, setEditingItemId] = useState<number | null>(null);
  const [editItemDesc, setEditItemDesc] = useState('');

  const fetchNotes = useCallback(async () => {
    const params = new URLSearchParams();
    if (noteSearch) params.set('q', noteSearch);
    const res = await fetch(`/api/notes?${params}`);
    const data = await res.json();
    setNotes(data);
  }, [noteSearch]);

  const fetchActionItems = useCallback(async () => {
    const params = new URLSearchParams();
    if (completedFilter !== 'all') params.set('completed', completedFilter);
    const res = await fetch(`/api/action-items?${params}`);
    const data = await res.json();
    setActionItems(data);
  }, [completedFilter]);

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  useEffect(() => {
    fetchActionItems();
  }, [fetchActionItems]);

  const createNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteTitle.trim()) return;
    await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: noteTitle, content: noteContent }),
    });
    setNoteTitle('');
    setNoteContent('');
    fetchNotes();
  };

  const deleteNote = async (id: number) => {
    await fetch(`/api/notes/${id}`, { method: 'DELETE' });
    fetchNotes();
  };

  const startEditNote = (note: Note) => {
    setEditingNoteId(note.id);
    setEditNoteTitle(note.title);
    setEditNoteContent(note.content);
  };

  const saveEditNote = async (id: number) => {
    await fetch(`/api/notes/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: editNoteTitle, content: editNoteContent }),
    });
    setEditingNoteId(null);
    fetchNotes();
  };

  const createActionItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actionDesc.trim()) return;
    await fetch('/api/action-items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description: actionDesc }),
    });
    setActionDesc('');
    fetchActionItems();
  };

  const deleteActionItem = async (id: number) => {
    await fetch(`/api/action-items/${id}`, { method: 'DELETE' });
    fetchActionItems();
  };

  const startEditItem = (item: ActionItem) => {
    setEditingItemId(item.id);
    setEditItemDesc(item.description);
  };

  const saveEditItem = async (id: number) => {
    await fetch(`/api/action-items/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description: editItemDesc }),
    });
    setEditingItemId(null);
    fetchActionItems();
  };

  const toggleComplete = async (item: ActionItem) => {
    if (item.completed) {
      await fetch(`/api/action-items/${item.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: false }),
      });
    } else {
      await fetch(`/api/action-items/${item.id}/complete`, { method: 'PUT' });
    }
    fetchActionItems();
  };

  return (
    <main>
      <h1>Notes &amp; Action Items Manager</h1>

      <section>
        <h2>Notes</h2>
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search notes..."
            value={noteSearch}
            onChange={(e) => setNoteSearch(e.target.value)}
          />
        </div>
        <form onSubmit={createNote}>
          <input
            type="text"
            placeholder="Title"
            value={noteTitle}
            onChange={(e) => setNoteTitle(e.target.value)}
            required
          />
          <textarea
            placeholder="Content"
            value={noteContent}
            onChange={(e) => setNoteContent(e.target.value)}
          />
          <button type="submit">Add Note</button>
        </form>
        <ul>
          {notes.map((note) => (
            <li key={note.id}>
              {editingNoteId === note.id ? (
                <>
                  <input
                    type="text"
                    value={editNoteTitle}
                    onChange={(e) => setEditNoteTitle(e.target.value)}
                  />
                  <textarea
                    value={editNoteContent}
                    onChange={(e) => setEditNoteContent(e.target.value)}
                  />
                  <button onClick={() => saveEditNote(note.id)}>Save</button>
                  <button onClick={() => setEditingNoteId(null)}>Cancel</button>
                </>
              ) : (
                <>
                  <strong>{note.title}</strong>: {note.content}
                  <button onClick={() => startEditNote(note)} style={{ marginLeft: '0.5rem', fontSize: '0.8rem' }}>Edit</button>
                  <button onClick={() => deleteNote(note.id)} style={{ marginLeft: '0.5rem', fontSize: '0.8rem' }}>Delete</button>
                </>
              )}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2>Action Items</h2>
        <div className="search-bar">
          <select
            value={completedFilter}
            onChange={(e) => setCompletedFilter(e.target.value)}
          >
            <option value="all">All</option>
            <option value="true">Completed</option>
            <option value="false">Pending</option>
          </select>
        </div>
        <form onSubmit={createActionItem}>
          <input
            type="text"
            placeholder="Description"
            value={actionDesc}
            onChange={(e) => setActionDesc(e.target.value)}
            required
          />
          <button type="submit">Add Item</button>
        </form>
        <ul>
          {actionItems.map((item) => (
            <li key={item.id} className={item.completed ? 'completed' : ''}>
              {editingItemId === item.id ? (
                <>
                  <input
                    type="text"
                    value={editItemDesc}
                    onChange={(e) => setEditItemDesc(e.target.value)}
                  />
                  <button onClick={() => saveEditItem(item.id)}>Save</button>
                  <button onClick={() => setEditingItemId(null)}>Cancel</button>
                </>
              ) : (
                <>
                  {item.description}
                  <button
                    onClick={() => toggleComplete(item)}
                    style={{ marginLeft: '0.5rem', fontSize: '0.8rem' }}
                  >
                    {item.completed ? 'Reopen' : 'Complete'}
                  </button>
                  <button onClick={() => startEditItem(item)} style={{ marginLeft: '0.5rem', fontSize: '0.8rem' }}>Edit</button>
                  <button onClick={() => deleteActionItem(item.id)} style={{ marginLeft: '0.5rem', fontSize: '0.8rem' }}>Delete</button>
                </>
              )}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
