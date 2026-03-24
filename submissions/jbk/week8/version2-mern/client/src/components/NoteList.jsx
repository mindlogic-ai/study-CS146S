import { useEffect, useState } from "react";
import { getNotes } from "../api";
import NoteForm from "./NoteForm";

export default function NoteList() {
  const [notes, setNotes] = useState([]);
  const [search, setSearch] = useState("");

  const load = async (params = {}) => {
    const data = await getNotes(params);
    setNotes(data);
  };

  useEffect(() => {
    load();
  }, []);

  const handleSearch = () => {
    load({ q: search });
  };

  return (
    <section>
      <h2>Notes</h2>
      <NoteForm onCreated={() => load()} />
      <div style={{ margin: ".25rem 0" }}>
        <input
          placeholder="Search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      <ul>
        {notes.map((n) => (
          <li key={n._id}>
            {n.title}: {n.content}
          </li>
        ))}
      </ul>
    </section>
  );
}
