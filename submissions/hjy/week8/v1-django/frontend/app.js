async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

async function loadNotes(params = {}) {
  const list = document.getElementById("notes");
  list.innerHTML = "";
  const query = new URLSearchParams(params);
  const notes = await fetchJSON("/api/notes/?" + query.toString());
  for (const n of notes) {
    const li = document.createElement("li");

    const text = document.createElement("span");
    text.textContent = `${n.title}: ${n.content}`;
    li.appendChild(text);

    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.style.marginLeft = "0.5rem";
    editBtn.onclick = () => {
      text.innerHTML = "";
      const titleInput = document.createElement("input");
      titleInput.value = n.title;
      titleInput.style.marginRight = "0.25rem";
      const contentInput = document.createElement("input");
      contentInput.value = n.content;
      contentInput.style.marginRight = "0.25rem";
      const saveBtn = document.createElement("button");
      saveBtn.textContent = "Save";
      saveBtn.onclick = async () => {
        await fetchJSON(`/api/notes/${n.id}/`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: titleInput.value, content: contentInput.value }),
        });
        loadNotes(params);
      };
      const cancelBtn = document.createElement("button");
      cancelBtn.textContent = "Cancel";
      cancelBtn.style.marginLeft = "0.25rem";
      cancelBtn.onclick = () => loadNotes(params);
      text.appendChild(titleInput);
      text.appendChild(contentInput);
      text.appendChild(saveBtn);
      text.appendChild(cancelBtn);
      editBtn.style.display = "none";
      delBtn.style.display = "none";
    };
    li.appendChild(editBtn);

    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";
    delBtn.style.marginLeft = "0.25rem";
    delBtn.onclick = async () => {
      await fetchJSON(`/api/notes/${n.id}/`, { method: "DELETE" });
      loadNotes(params);
    };
    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

async function loadActions(params = {}) {
  const list = document.getElementById("actions");
  list.innerHTML = "";
  const query = new URLSearchParams(params);
  const items = await fetchJSON("/api/action-items/?" + query.toString());
  for (const a of items) {
    const li = document.createElement("li");
    li.textContent = `${a.description} [${a.completed ? "done" : "open"}]`;

    const toggleBtn = document.createElement("button");
    toggleBtn.textContent = a.completed ? "Reopen" : "Complete";
    toggleBtn.onclick = async () => {
      await fetchJSON(`/api/action-items/${a.id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completed: !a.completed }),
      });
      loadActions(params);
    };
    li.appendChild(toggleBtn);

    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";
    delBtn.style.marginLeft = "0.25rem";
    delBtn.onclick = async () => {
      await fetchJSON(`/api/action-items/${a.id}/`, { method: "DELETE" });
      loadActions(params);
    };
    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("note-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("note-title").value;
    const content = document.getElementById("note-content").value;
    await fetchJSON("/api/notes/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById("note-search-btn").addEventListener("click", async () => {
    const q = document.getElementById("note-search").value;
    loadNotes({ q });
  });

  document.getElementById("action-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const description = document.getElementById("action-desc").value;
    await fetchJSON("/api/action-items/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  document.getElementById("filter-completed").addEventListener("change", (e) => {
    const checked = e.target.checked;
    loadActions(checked ? { completed: true } : {});
  });

  loadNotes();
  loadActions();
});
