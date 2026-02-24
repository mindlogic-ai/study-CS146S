async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const notes = await fetchJSON('/notes/');
  for (const n of notes) {
    const li = document.createElement('li');
    li.dataset.id = n.id;

    const span = document.createElement('span');
    span.textContent = `${n.title}: ${n.content}`;
    li.appendChild(span);

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = () => startEdit(li, n);
    li.appendChild(editBtn);

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.className = 'delete-btn';
    delBtn.onclick = async () => {
      await fetchJSON(`/notes/${n.id}`, { method: 'DELETE' });
      loadNotes();
    };
    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

function startEdit(li, note) {
  li.innerHTML = '';
  const titleInput = document.createElement('input');
  titleInput.value = note.title;
  titleInput.placeholder = 'Title';

  const contentInput = document.createElement('input');
  contentInput.value = note.content;
  contentInput.placeholder = 'Content';

  const saveBtn = document.createElement('button');
  saveBtn.textContent = 'Save';
  saveBtn.onclick = async () => {
    await fetchJSON(`/notes/${note.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: titleInput.value, content: contentInput.value }),
    });
    loadNotes();
  };

  const cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Cancel';
  cancelBtn.onclick = () => loadNotes();

  li.appendChild(titleInput);
  li.appendChild(contentInput);
  li.appendChild(saveBtn);
  li.appendChild(cancelBtn);
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

  loadNotes();
  loadActions();
});
