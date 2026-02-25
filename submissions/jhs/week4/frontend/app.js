async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const notes = await fetchJSON('/notes/');
  for (const n of notes) {
    const li = document.createElement('li');

    const text = document.createElement('span');
    text.textContent = `${n.title}: ${n.content}`;
    li.appendChild(text);

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = async () => {
      const newTitle = prompt('New title:', n.title);
      if (newTitle === null) return;
      const newContent = prompt('New content:', n.content);
      if (newContent === null) return;
      const body = {};
      if (newTitle !== n.title) body.title = newTitle;
      if (newContent !== n.content) body.content = newContent;
      if (Object.keys(body).length > 0) {
        await fetchJSON(`/notes/${n.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        loadNotes();
      }
    };
    li.appendChild(editBtn);

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.className = 'danger';
    delBtn.onclick = async () => {
      if (!confirm(`Delete "${n.title}"?`)) return;
      await fetchJSON(`/notes/${n.id}`, { method: 'DELETE' });
      loadNotes();
    };
    li.appendChild(delBtn);

    const extractBtn = document.createElement('button');
    extractBtn.textContent = 'Extract';
    extractBtn.onclick = async () => {
      const result = await fetchJSON(`/notes/${n.id}/extract`, { method: 'POST' });
      let msg = 'Extracted:\n';
      msg += `Action items: ${result.action_items.length ? result.action_items.join(', ') : 'none'}\n`;
      msg += `Tags: ${result.tags.length ? result.tags.map(t => '#' + t).join(', ') : 'none'}`;
      alert(msg);
    };
    li.appendChild(extractBtn);

    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.className = 'danger';
    delBtn.onclick = async () => {
      if (!confirm(`Delete "${a.description}"?`)) return;
      await fetchJSON(`/action-items/${a.id}`, { method: 'DELETE' });
      loadActions();
    };
    li.appendChild(delBtn);
    list.appendChild(li);
  }
}

async function searchNotes(query) {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const url = query ? `/notes/search/?q=${encodeURIComponent(query)}` : '/notes/';
  const notes = await fetchJSON(url);
  for (const n of notes) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  document.getElementById('search-btn').addEventListener('click', () => {
    const q = document.getElementById('search-input').value.trim();
    searchNotes(q);
  });

  loadNotes();
  loadActions();
});
