import { useState } from "react";

function ActionItemList({ items, onComplete, onReopen, onDelete, onEdit, completedFilter, onFilterChange }) {
  const [editingId, setEditingId] = useState(null);
  const [editDesc, setEditDesc] = useState("");

  const startEdit = (item) => {
    setEditingId(item.id);
    setEditDesc(item.description);
  };

  const cancelEdit = () => {
    setEditingId(null);
  };

  const saveEdit = (id) => {
    onEdit(id, { description: editDesc });
    setEditingId(null);
  };

  return (
    <div>
      <div className="filter-row">
        <label>Filter: </label>
        <select value={completedFilter} onChange={(e) => onFilterChange(e.target.value)}>
          <option value="all">All</option>
          <option value="true">Completed</option>
          <option value="false">Pending</option>
        </select>
      </div>
      {items.length === 0 ? (
        <p className="empty">No action items.</p>
      ) : (
        items.map((item) => (
          <div
            key={item.id}
            className={`action-item ${item.completed ? "completed" : ""}`}
          >
            {editingId === item.id ? (
              <>
                <input
                  type="text"
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                />
                <button className="success" onClick={() => saveEdit(item.id)}>Save</button>
                <button onClick={cancelEdit}>Cancel</button>
              </>
            ) : (
              <>
                <span>{item.description}</span>
                <div className="item-time">
                  {new Date(item.created_at).toLocaleString()}
                </div>
                <button onClick={() => startEdit(item)}>Edit</button>
                <button className="warning" onClick={() => onDelete(item.id)}>Delete</button>
                {item.completed ? (
                  <button className="warning" onClick={() => onReopen(item.id)}>
                    Reopen
                  </button>
                ) : (
                  <button className="success" onClick={() => onComplete(item.id)}>
                    Complete
                  </button>
                )}
              </>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default ActionItemList;
