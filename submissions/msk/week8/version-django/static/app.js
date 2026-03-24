const API = "/api";

async function apiCall(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }
  if (res.status === 204) return null;
  return res.json();
}

// --- Notes ---
async function loadNotes(search = "") {
  const params = search ? `?q=${encodeURIComponent(search)}` : "";
  const data = await apiCall(`${API}/notes/${params}`);
  const notes = data.results || data;
  const ul = document.getElementById("notes");
  ul.innerHTML = "";
  notes.forEach((note) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <div class="item-content">
        <h3>${escapeHtml(note.title)}</h3>
        <p>${escapeHtml(note.content)}</p>
        <div class="timestamp">Updated: ${new Date(note.updated_at).toLocaleString()}</div>
      </div>
      <div class="item-actions">
        <button class="secondary" onclick="editNote(${note.id})">Edit</button>
        <button class="danger" onclick="deleteNote(${note.id})">Delete</button>
      </div>`;
    li.id = `note-${note.id}`;
    li.dataset.title = note.title;
    li.dataset.content = note.content;
    ul.appendChild(li);
  });
}

document.getElementById("note-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("note-title").value.trim();
  const content = document.getElementById("note-content").value.trim();
  if (!title || !content) return;
  await apiCall(`${API}/notes/`, {
    method: "POST",
    body: JSON.stringify({ title, content }),
  });
  document.getElementById("note-title").value = "";
  document.getElementById("note-content").value = "";
  loadNotes();
});

document.getElementById("note-search-btn").addEventListener("click", () => {
  loadNotes(document.getElementById("note-search").value);
});

document.getElementById("note-search").addEventListener("keyup", (e) => {
  if (e.key === "Enter") loadNotes(e.target.value);
});

async function deleteNote(id) {
  await apiCall(`${API}/notes/${id}/`, { method: "DELETE" });
  loadNotes();
}

function editNote(id) {
  const li = document.getElementById(`note-${id}`);
  const title = li.dataset.title;
  const content = li.dataset.content;
  li.innerHTML = `
    <form class="edit-form" onsubmit="saveNote(event, ${id})">
      <input id="edit-title-${id}" value="${escapeAttr(title)}" required />
      <textarea id="edit-content-${id}" required>${escapeHtml(content)}</textarea>
      <button type="submit">Save</button>
      <button type="button" class="secondary" onclick="loadNotes()">Cancel</button>
    </form>`;
}

async function saveNote(e, id) {
  e.preventDefault();
  const title = document.getElementById(`edit-title-${id}`).value.trim();
  const content = document.getElementById(`edit-content-${id}`).value.trim();
  await apiCall(`${API}/notes/${id}/`, {
    method: "PATCH",
    body: JSON.stringify({ title, content }),
  });
  loadNotes();
}

// --- Action Items ---
async function loadActions(completedOnly = false) {
  const params = completedOnly ? "?completed=true" : "";
  const data = await apiCall(`${API}/action-items/${params}`);
  const items = data.results || data;
  const ul = document.getElementById("actions");
  ul.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    const cls = item.completed ? "completed-text" : "";
    li.innerHTML = `
      <div class="item-content">
        <p class="${cls}">${escapeHtml(item.description)}</p>
        <div class="timestamp">Updated: ${new Date(item.updated_at).toLocaleString()}</div>
      </div>
      <div class="item-actions">
        <button class="secondary" onclick="toggleAction(${item.id}, ${!item.completed})">
          ${item.completed ? "Undo" : "Done"}
        </button>
        <button class="secondary" onclick="editAction(${item.id}, '${escapeAttr(item.description)}')">Edit</button>
        <button class="danger" onclick="deleteAction(${item.id})">Delete</button>
      </div>`;
    li.id = `action-${item.id}`;
    ul.appendChild(li);
  });
}

document.getElementById("action-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const desc = document.getElementById("action-desc").value.trim();
  if (!desc) return;
  await apiCall(`${API}/action-items/`, {
    method: "POST",
    body: JSON.stringify({ description: desc }),
  });
  document.getElementById("action-desc").value = "";
  loadActions(document.getElementById("filter-completed").checked);
});

document.getElementById("filter-completed").addEventListener("change", (e) => {
  loadActions(e.target.checked);
});

async function toggleAction(id, completed) {
  await apiCall(`${API}/action-items/${id}/`, {
    method: "PATCH",
    body: JSON.stringify({ completed }),
  });
  loadActions(document.getElementById("filter-completed").checked);
}

async function deleteAction(id) {
  await apiCall(`${API}/action-items/${id}/`, { method: "DELETE" });
  loadActions(document.getElementById("filter-completed").checked);
}

function editAction(id, currentDesc) {
  const li = document.getElementById(`action-${id}`);
  li.innerHTML = `
    <form class="edit-form" onsubmit="saveAction(event, ${id})">
      <input id="edit-action-${id}" value="${escapeAttr(currentDesc)}" required />
      <button type="submit">Save</button>
      <button type="button" class="secondary" onclick="loadActions(document.getElementById('filter-completed').checked)">Cancel</button>
    </form>`;
}

async function saveAction(e, id) {
  e.preventDefault();
  const description = document.getElementById(`edit-action-${id}`).value.trim();
  await apiCall(`${API}/action-items/${id}/`, {
    method: "PATCH",
    body: JSON.stringify({ description }),
  });
  loadActions(document.getElementById("filter-completed").checked);
}

// --- Helpers ---
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function escapeAttr(str) {
  return str.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#39;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// --- Init ---
loadNotes();
loadActions();
