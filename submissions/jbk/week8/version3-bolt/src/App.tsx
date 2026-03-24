import { useState, useEffect } from 'react';
import { Search, Plus, CheckCircle2, Circle } from 'lucide-react';
import { Note, ActionItem } from './types';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;

function App() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [actionDescription, setActionDescription] = useState('');
  const [showCompletedOnly, setShowCompletedOnly] = useState(false);

  const fetchNotes = async (query = '') => {
    const url = `${SUPABASE_URL}/functions/v1/notes${query ? `?q=${encodeURIComponent(query)}` : ''}`;
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    setNotes(data);
  };

  const fetchActionItems = async (completed?: boolean) => {
    const url = `${SUPABASE_URL}/functions/v1/action-items${completed !== undefined ? `?completed=${completed}` : ''}`;
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    setActionItems(data);
  };

  useEffect(() => {
    fetchNotes();
    fetchActionItems();
  }, []);

  const handleAddNote = async () => {
    if (!noteTitle.trim() || !noteContent.trim()) return;

    await fetch(`${SUPABASE_URL}/functions/v1/notes`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title: noteTitle, content: noteContent }),
    });

    setNoteTitle('');
    setNoteContent('');
    fetchNotes(searchQuery);
  };

  const handleSearch = () => {
    fetchNotes(searchQuery);
  };

  const handleAddActionItem = async () => {
    if (!actionDescription.trim()) return;

    await fetch(`${SUPABASE_URL}/functions/v1/action-items`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ description: actionDescription }),
    });

    setActionDescription('');
    fetchActionItems(showCompletedOnly ? true : undefined);
  };

  const handleToggleComplete = async (id: string, currentStatus: boolean) => {
    if (!currentStatus) {
      await fetch(`${SUPABASE_URL}/functions/v1/action-items/${id}/complete`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
      });
    } else {
      await fetch(`${SUPABASE_URL}/functions/v1/action-items/${id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ completed: false }),
      });
    }

    fetchActionItems(showCompletedOnly ? true : undefined);
  };

  const handleFilterChange = (checked: boolean) => {
    setShowCompletedOnly(checked);
    fetchActionItems(checked ? true : undefined);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-semibold text-gray-900 mb-8">Notes & Action Items</h1>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Notes</h2>

            <div className="space-y-3 mb-6">
              <input
                type="text"
                placeholder="Title (max 200 chars)"
                maxLength={200}
                value={noteTitle}
                onChange={(e) => setNoteTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <textarea
                placeholder="Content"
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleAddNote}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <Plus size={20} />
                Add Note
              </button>
            </div>

            <div className="mb-6">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Search notes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSearch}
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors flex items-center gap-2"
                >
                  <Search size={20} />
                  Search
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {notes.map((note) => (
                <div key={note.id} className="p-3 bg-gray-50 rounded-md border border-gray-200">
                  <p className="text-sm text-gray-900">
                    <span className="font-semibold">{note.title}:</span> {note.content}
                  </p>
                </div>
              ))}
              {notes.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-4">No notes found</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Action Items</h2>

            <div className="space-y-3 mb-6">
              <textarea
                placeholder="Description"
                value={actionDescription}
                onChange={(e) => setActionDescription(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button
                onClick={handleAddActionItem}
                className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
              >
                <Plus size={20} />
                Add Action Item
              </button>
            </div>

            <div className="mb-6">
              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showCompletedOnly}
                  onChange={(e) => handleFilterChange(e.target.checked)}
                  className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                />
                Show completed only
              </label>
            </div>

            <div className="space-y-3">
              {actionItems.map((item) => (
                <div key={item.id} className="p-3 bg-gray-50 rounded-md border border-gray-200 flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      {item.description}{' '}
                      <span className={`font-semibold ${item.completed ? 'text-green-600' : 'text-orange-600'}`}>
                        [{item.completed ? 'done' : 'open'}]
                      </span>
                    </p>
                  </div>
                  <button
                    onClick={() => handleToggleComplete(item.id, item.completed)}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${
                      item.completed
                        ? 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {item.completed ? (
                      <>
                        <Circle size={16} />
                        Reopen
                      </>
                    ) : (
                      <>
                        <CheckCircle2 size={16} />
                        Complete
                      </>
                    )}
                  </button>
                </div>
              ))}
              {actionItems.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-4">No action items found</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
