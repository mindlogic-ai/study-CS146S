import { useEffect, useState } from "react";
import { getActionItems, completeActionItem, patchActionItem } from "../api";
import ActionItemForm from "./ActionItemForm";

export default function ActionItemList() {
  const [items, setItems] = useState([]);
  const [filterCompleted, setFilterCompleted] = useState(false);

  const load = async (params = {}) => {
    const data = await getActionItems(params);
    setItems(data);
  };

  useEffect(() => {
    if (filterCompleted) {
      load({ completed: true });
    } else {
      load();
    }
  }, [filterCompleted]);

  const handleComplete = async (id) => {
    await completeActionItem(id);
    load(filterCompleted ? { completed: true } : {});
  };

  const handleReopen = async (id) => {
    await patchActionItem(id, { completed: false });
    load(filterCompleted ? { completed: true } : {});
  };

  return (
    <section>
      <h2>Action Items</h2>
      <ActionItemForm
        onCreated={() => load(filterCompleted ? { completed: true } : {})}
      />
      <div style={{ margin: ".25rem 0" }}>
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
        {items.map((a) => (
          <li key={a._id}>
            {a.description} [{a.completed ? "done" : "open"}]
            {!a.completed ? (
              <button onClick={() => handleComplete(a._id)}>Complete</button>
            ) : (
              <button onClick={() => handleReopen(a._id)}>Reopen</button>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
