import { useState, useEffect } from 'react';
import { supabase, ActionItem } from '../lib/supabase';
import { Plus, Trash2, Circle, CheckCircle2 } from 'lucide-react';

export function ActionItems() {
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<ActionItem[]>([]);
  const [newDescription, setNewDescription] = useState('');
  const [filter, setFilter] = useState<'all' | 'completed'>('all');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchActionItems();
  }, []);

  useEffect(() => {
    if (filter === 'all') {
      setFilteredItems(actionItems);
    } else {
      setFilteredItems(actionItems.filter((item) => item.completed));
    }
  }, [filter, actionItems]);

  const fetchActionItems = async () => {
    try {
      const { data, error } = await supabase
        .from('action_items')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      setActionItems(data || []);
    } catch (err) {
      setError('Failed to fetch action items');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createActionItem = async () => {
    if (!newDescription.trim()) {
      setError('Description is required');
      return;
    }

    try {
      const { error } = await supabase
        .from('action_items')
        .insert([{ description: newDescription.trim() }]);

      if (error) throw error;

      setNewDescription('');
      setError('');
      fetchActionItems();
    } catch (err) {
      setError('Failed to create action item');
      console.error(err);
    }
  };

  const toggleComplete = async (id: string, currentStatus: boolean) => {
    try {
      const { error } = await supabase
        .from('action_items')
        .update({ completed: !currentStatus })
        .eq('id', id);

      if (error) throw error;
      fetchActionItems();
    } catch (err) {
      setError('Failed to update action item');
      console.error(err);
    }
  };

  const deleteActionItem = async (id: string) => {
    try {
      const { error } = await supabase
        .from('action_items')
        .delete()
        .eq('id', id);

      if (error) throw error;
      fetchActionItems();
    } catch (err) {
      setError('Failed to delete action item');
      console.error(err);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading action items...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Action Items
        </h2>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
          <textarea
            placeholder="Action item description"
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md mb-2 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
            rows={2}
          />
          <button
            onClick={createActionItem}
            className="w-full bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition-colors flex items-center justify-center gap-2"
          >
            <Plus size={18} />
            Add Action Item
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-md mb-4">
            {error}
          </div>
        )}

        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setFilter('all')}
            className={`flex-1 px-4 py-2 rounded-md transition-colors ${
              filter === 'all'
                ? 'bg-green-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`flex-1 px-4 py-2 rounded-md transition-colors ${
              filter === 'completed'
                ? 'bg-green-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Completed
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {filteredItems.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            {filter === 'completed'
              ? 'No completed items yet'
              : 'No action items yet. Create your first item above!'}
          </div>
        ) : (
          filteredItems.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
            >
              <div className="flex items-start gap-3">
                <button
                  onClick={() => toggleComplete(item.id, item.completed)}
                  className="flex-shrink-0 mt-1 transition-colors"
                >
                  {item.completed ? (
                    <CheckCircle2
                      size={22}
                      className="text-green-500 hover:text-green-600"
                    />
                  ) : (
                    <Circle
                      size={22}
                      className="text-gray-400 hover:text-gray-600"
                    />
                  )}
                </button>
                <div className="flex-1">
                  <p
                    className={`text-gray-800 ${
                      item.completed
                        ? 'line-through text-gray-500'
                        : ''
                    }`}
                  >
                    {item.description}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {formatDate(item.created_at)}
                  </p>
                </div>
                <button
                  onClick={() => deleteActionItem(item.id)}
                  className="flex-shrink-0 text-red-500 hover:text-red-700 transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
