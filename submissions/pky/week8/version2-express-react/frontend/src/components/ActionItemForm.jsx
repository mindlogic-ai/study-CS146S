import { useState } from "react";

function ActionItemForm({ onSubmit }) {
  const [description, setDescription] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) return;
    await onSubmit({ description: description.trim() });
    setDescription("");
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-row">
        <input
          type="text"
          placeholder="Action item description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button type="submit" className="primary">
          Add Item
        </button>
      </div>
    </form>
  );
}

export default ActionItemForm;
