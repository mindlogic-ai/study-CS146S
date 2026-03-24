import { useState } from "react";

function NoteForm({ onSubmit }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    await onSubmit({ title: title.trim(), content: content.trim() });
    setTitle("");
    setContent("");
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-row">
        <input
          type="text"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>
      <div className="form-row">
        <textarea
          placeholder="Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <button type="submit" className="primary">
          Add Note
        </button>
      </div>
    </form>
  );
}

export default NoteForm;
