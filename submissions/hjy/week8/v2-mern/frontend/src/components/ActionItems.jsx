import { useState, useEffect } from "react";

const API = "/api/action-items";

function ActionItems() {
  const [items, setItems] = useState([]);
  const [description, setDescription] = useState("");
  const [filter, setFilter] = useState("all"); // "all" | "active" | "completed"
  const [editingId, setEditingId] = useState(null);
  const [editDescription, setEditDescription] = useState("");

  const fetchItems = async () => {
    let params = "";
    if (filter === "active") params = "?completed=false";
    else if (filter === "completed") params = "?completed=true";
    const res = await fetch(`${API}${params}`);
    const data = await res.json();
    setItems(data);
  };

  useEffect(() => {
    fetchItems();
  }, [filter]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!description.trim()) return;
    await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: description.trim() }),
    });
    setDescription("");
    fetchItems();
  };

  const handleToggle = async (item) => {
    await fetch(`${API}/${item._id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: !item.completed }),
    });
    fetchItems();
  };

  const handleDelete = async (id) => {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    fetchItems();
  };

  const startEdit = (item) => {
    setEditingId(item._id);
    setEditDescription(item.description);
  };

  const handleUpdate = async (id) => {
    await fetch(`${API}/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: editDescription.trim() }),
    });
    setEditingId(null);
    fetchItems();
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString();
  };

  return (
    <div>
      <h2>Action Items</h2>

      <form className="form" onSubmit={handleCreate}>
        <input
          type="text"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button type="submit" className="btn btn-primary">
          Add Item
        </button>
      </form>

      <div className="filter-bar">
        <button
          className={filter === "all" ? "active" : ""}
          onClick={() => setFilter("all")}
        >
          All
        </button>
        <button
          className={filter === "active" ? "active" : ""}
          onClick={() => setFilter("active")}
        >
          Active
        </button>
        <button
          className={filter === "completed" ? "active" : ""}
          onClick={() => setFilter("completed")}
        >
          Completed
        </button>
      </div>

      {items.length === 0 ? (
        <p className="empty">No action items found.</p>
      ) : (
        items.map((item) => (
          <div
            key={item._id}
            className={`card ${item.completed ? "completed" : ""}`}
          >
            {editingId === item._id ? (
              <div className="edit-form">
                <input
                  type="text"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                />
                <div className="edit-actions">
                  <button
                    className="btn btn-sm btn-primary"
                    onClick={() => handleUpdate(item._id)}
                  >
                    Save
                  </button>
                  <button
                    className="btn btn-sm"
                    onClick={() => setEditingId(null)}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="card-header">
                  <span className={item.completed ? "description" : ""}>
                    {item.description}
                  </span>
                  <div className="card-actions">
                    <button
                      className={`btn btn-sm ${item.completed ? "btn-warning" : "btn-success"}`}
                      onClick={() => handleToggle(item)}
                    >
                      {item.completed ? "Reopen" : "Complete"}
                    </button>
                    <button
                      className="btn btn-sm btn-warning"
                      onClick={() => startEdit(item)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(item._id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <span className="meta">
                  Created: {formatDate(item.createdAt)}
                  {item.updatedAt !== item.createdAt &&
                    ` | Updated: ${formatDate(item.updatedAt)}`}
                </span>
              </>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default ActionItems;
