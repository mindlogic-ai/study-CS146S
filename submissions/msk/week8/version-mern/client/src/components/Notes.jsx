import { useState, useEffect, useCallback } from "react";

const API = "/api/notes";

function Notes() {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [search, setSearch] = useState("");
  const [editId, setEditId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");

  const loadNotes = useCallback(async () => {
    const params = search ? `?q=${encodeURIComponent(search)}` : "";
    const res = await fetch(`${API}${params}`);
    setNotes(await res.json());
  }, [search]);

  useEffect(() => {
    loadNotes();
  }, [loadNotes]);

  const addNote = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: title.trim(), content: content.trim() }),
    });
    setTitle("");
    setContent("");
    loadNotes();
  };

  const deleteNote = async (id) => {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    loadNotes();
  };

  const startEdit = (note) => {
    setEditId(note._id);
    setEditTitle(note.title);
    setEditContent(note.content);
  };

  const saveEdit = async (e) => {
    e.preventDefault();
    await fetch(`${API}/${editId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: editTitle.trim(),
        content: editContent.trim(),
      }),
    });
    setEditId(null);
    loadNotes();
  };

  return (
    <section>
      <h2>Notes</h2>
      <form onSubmit={addNote}>
        <input
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <textarea
          placeholder="Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
        <button type="submit">Add Note</button>
      </form>
      <div className="controls">
        <input
          placeholder="Search notes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyUp={(e) => e.key === "Enter" && loadNotes()}
        />
        <button onClick={loadNotes}>Search</button>
      </div>
      <ul>
        {notes.map((note) => (
          <li key={note._id}>
            {editId === note._id ? (
              <form className="edit-form" onSubmit={saveEdit}>
                <input
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  required
                />
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  required
                />
                <button type="submit">Save</button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setEditId(null)}
                >
                  Cancel
                </button>
              </form>
            ) : (
              <>
                <div className="item-content">
                  <h3>{note.title}</h3>
                  <p>{note.content}</p>
                  <div className="timestamp">
                    Updated: {new Date(note.updatedAt).toLocaleString()}
                  </div>
                </div>
                <div className="item-actions">
                  <button className="secondary" onClick={() => startEdit(note)}>
                    Edit
                  </button>
                  <button
                    className="danger"
                    onClick={() => deleteNote(note._id)}
                  >
                    Delete
                  </button>
                </div>
              </>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default Notes;
