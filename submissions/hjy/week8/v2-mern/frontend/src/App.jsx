import { useState } from "react";
import Notes from "./components/Notes.jsx";
import ActionItems from "./components/ActionItems.jsx";

function App() {
  const [activeTab, setActiveTab] = useState("notes");

  return (
    <div className="app">
      <h1>Notes & Action Items</h1>
      <div className="tabs">
        <button
          className={activeTab === "notes" ? "active" : ""}
          onClick={() => setActiveTab("notes")}
        >
          Notes
        </button>
        <button
          className={activeTab === "actions" ? "active" : ""}
          onClick={() => setActiveTab("actions")}
        >
          Action Items
        </button>
      </div>
      {activeTab === "notes" ? <Notes /> : <ActionItems />}
    </div>
  );
}

export default App;
