import { useState, useEffect, useCallback } from "react";
import { notesApi, actionItemsApi } from "./api.js";
import NoteForm from "./components/NoteForm.jsx";
import NoteList from "./components/NoteList.jsx";
import ActionItemForm from "./components/ActionItemForm.jsx";
import ActionItemList from "./components/ActionItemList.jsx";

function App() {
  const [notes, setNotes] = useState([]);
  const [actionItems, setActionItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [completedFilter, setCompletedFilter] = useState("all");

  const loadNotes = useCallback(async () => {
    const params = {};
    if (searchQuery) params.q = searchQuery;
    const data = await notesApi.list(params);
    setNotes(data);
  }, [searchQuery]);

  const loadActionItems = useCallback(async () => {
    const params = {};
    if (completedFilter !== "all") params.completed = completedFilter;
    const data = await actionItemsApi.list(params);
    setActionItems(data);
  }, [completedFilter]);

  useEffect(() => {
    loadNotes();
  }, [loadNotes]);

  useEffect(() => {
    loadActionItems();
  }, [loadActionItems]);

  const handleCreateNote = async (noteData) => {
    await notesApi.create(noteData);
    loadNotes();
  };

  const handleEditNote = async (id, data) => {
    await notesApi.update(id, data);
    loadNotes();
  };

  const handleDeleteNote = async (id) => {
    await notesApi.delete(id);
    loadNotes();
  };

  const handleCreateActionItem = async (itemData) => {
    await actionItemsApi.create(itemData);
    loadActionItems();
  };

  const handleEditActionItem = async (id, data) => {
    await actionItemsApi.update(id, data);
    loadActionItems();
  };

  const handleDeleteActionItem = async (id) => {
    await actionItemsApi.delete(id);
    loadActionItems();
  };

  const handleCompleteItem = async (id) => {
    await actionItemsApi.complete(id);
    loadActionItems();
  };

  const handleReopenItem = async (id) => {
    await actionItemsApi.update(id, { completed: false });
    loadActionItems();
  };

  const handleFilterChange = (value) => {
    setCompletedFilter(value);
  };

  return (
    <div className="container">
      <h1>Notes & Action Items</h1>

      <section className="card">
        <h2>Notes</h2>
        <NoteForm onSubmit={handleCreateNote} />
        <NoteList
          notes={notes}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onDelete={handleDeleteNote}
          onEdit={handleEditNote}
        />
      </section>

      <section className="card">
        <h2>Action Items</h2>
        <ActionItemForm onSubmit={handleCreateActionItem} />
        <ActionItemList
          items={actionItems}
          onComplete={handleCompleteItem}
          onReopen={handleReopenItem}
          onDelete={handleDeleteActionItem}
          onEdit={handleEditActionItem}
          completedFilter={completedFilter}
          onFilterChange={handleFilterChange}
        />
      </section>
    </div>
  );
}

export default App;
