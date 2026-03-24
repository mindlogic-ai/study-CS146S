import { useState, useEffect, useCallback } from "react";

const API = "/api/action-items";

function ActionItems() {
  const [items, setItems] = useState([]);
  const [description, setDescription] = useState("");
  const [filterCompleted, setFilterCompleted] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editDesc, setEditDesc] = useState("");

  const loadItems = useCallback(async () => {
    const params = filterCompleted ? "?completed=true" : "";
    const res = await fetch(`${API}${params}`);
    setItems(await res.json());
  }, [filterCompleted]);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  const addItem = async (e) => {
    e.preventDefault();
    if (!description.trim()) return;
    await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: description.trim() }),
    });
    setDescription("");
    loadItems();
  };

  const toggleComplete = async (id, completed) => {
    await fetch(`${API}/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed }),
    });
    loadItems();
  };

  const deleteItem = async (id) => {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    loadItems();
  };

  const startEdit = (item) => {
    setEditId(item._id);
    setEditDesc(item.description);
  };

  const saveEdit = async (e) => {
    e.preventDefault();
    await fetch(`${API}/${editId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: editDesc.trim() }),
    });
    setEditId(null);
    loadItems();
  };

  return (
    <section>
      <h2>Action Items</h2>
      <form onSubmit={addItem}>
        <input
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
        <button type="submit">Add Action Item</button>
      </form>
      <div className="controls">
        <label>
          <input
            type="checkbox"
            checked={filterCompleted}
            onChange={(e) => setFilterCompleted(e.target.checked)}
          />{" "}
          Show completed only
        </label>
      </div>
      <ul>
        {items.map((item) => (
          <li key={item._id}>
            {editId === item._id ? (
              <form className="edit-form" onSubmit={saveEdit}>
                <input
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
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
                  <p className={item.completed ? "completed-text" : ""}>
                    {item.description}
                  </p>
                  <div className="timestamp">
                    Updated: {new Date(item.updatedAt).toLocaleString()}
                  </div>
                </div>
                <div className="item-actions">
                  <button
                    className="secondary"
                    onClick={() =>
                      toggleComplete(item._id, !item.completed)
                    }
                  >
                    {item.completed ? "Undo" : "Done"}
                  </button>
                  <button
                    className="secondary"
                    onClick={() => startEdit(item)}
                  >
                    Edit
                  </button>
                  <button
                    className="danger"
                    onClick={() => deleteItem(item._id)}
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

export default ActionItems;
