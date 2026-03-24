import { useState } from "react";

function NoteList({ notes, searchQuery, onSearchChange, onDelete, onEdit }) {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");

  const startEdit = (note) => {
    setEditingId(note.id);
    setEditTitle(note.title);
    setEditContent(note.content);
  };

  const cancelEdit = () => {
    setEditingId(null);
  };

  const saveEdit = (id) => {
    onEdit(id, { title: editTitle, content: editContent });
    setEditingId(null);
  };

  return (
    <div>
      <input
        type="text"
        className="search-input"
        placeholder="Search notes..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
      />
      {notes.length === 0 ? (
        <p className="empty">No notes found.</p>
      ) : (
        notes.map((note) => (
          <div key={note.id} className="note-item">
            {editingId === note.id ? (
              <>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                />
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                />
                <button className="success" onClick={() => saveEdit(note.id)}>Save</button>
                <button onClick={cancelEdit}>Cancel</button>
              </>
            ) : (
              <>
                <h3>{note.title}</h3>
                <p>{note.content}</p>
                <div className="note-time">
                  {new Date(note.created_at).toLocaleString()}
                </div>
                <button onClick={() => startEdit(note)}>Edit</button>
                <button className="warning" onClick={() => onDelete(note.id)}>Delete</button>
              </>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default NoteList;
