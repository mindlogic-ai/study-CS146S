import { useState } from "react";
import { createActionItem } from "../api";

export default function ActionItemForm({ onCreated }) {
  const [description, setDescription] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createActionItem({ description });
    setDescription("");
    onCreated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      />
      <button type="submit">Add</button>
    </form>
  );
}
