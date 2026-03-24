async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

async function loadNotes(params = {}) {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const query = new URLSearchParams(params);
  const notes = await fetchJSON('/api/notes/?' + query.toString());
  for (const n of notes) {
    const li = document.createElement('li');

    const text = document.createElement('span');
    text.textContent = `${n.title}: ${n.content}`;
    li.appendChild(text);

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = () => {
      const newTitle = prompt('Edit title:', n.title);
      if (newTitle === null) return;
      const newContent = prompt('Edit content:', n.content);
      if (newContent === null) return;
      fetchJSON(`/api/notes/${n.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, content: newContent }),
      }).then(() => loadNotes(params));
    };
    li.appendChild(editBtn);

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.onclick = async () => {
      if (!confirm('Delete this note?')) return;
      await fetch(`/api/notes/${n.id}/`, { method: 'DELETE' });
      loadNotes(params);
    };
    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

async function loadActions(params = {}) {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const query = new URLSearchParams(params);
  const items = await fetchJSON('/api/action-items/?' + query.toString());
  for (const a of items) {
    const li = document.createElement('li');

    const text = document.createElement('span');
    text.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    li.appendChild(text);

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = () => {
      const newDesc = prompt('Edit description:', a.description);
      if (newDesc === null) return;
      fetchJSON(`/api/action-items/${a.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: newDesc }),
      }).then(() => loadActions(params));
    };
    li.appendChild(editBtn);

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.onclick = async () => {
      if (!confirm('Delete this action item?')) return;
      await fetch(`/api/action-items/${a.id}/`, { method: 'DELETE' });
      loadActions(params);
    };
    li.appendChild(delBtn);

    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/api/action-items/${a.id}/complete/`, { method: 'PUT' });
        loadActions(params);
      };
      li.appendChild(btn);
    } else {
      const btn = document.createElement('button');
      btn.textContent = 'Reopen';
      btn.onclick = async () => {
        await fetchJSON(`/api/action-items/${a.id}/`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ completed: false }),
        });
        loadActions(params);
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/api/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('note-search-btn').addEventListener('click', async () => {
    const q = document.getElementById('note-search').value;
    loadNotes({ q });
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/api/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  document.getElementById('filter-completed').addEventListener('change', (e) => {
    const checked = e.target.checked;
    loadActions({ completed: checked });
  });

  loadNotes();
  loadActions();
});
