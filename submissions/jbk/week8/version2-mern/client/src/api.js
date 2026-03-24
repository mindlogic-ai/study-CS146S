const BASE = "/api";

export async function fetchJSON(url, options) {
  const res = await fetch(BASE + url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function getNotes(params = {}) {
  const query = new URLSearchParams(params).toString();
  return fetchJSON(`/notes/?${query}`);
}

export function createNote(data) {
  return fetchJSON("/notes/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function patchNote(id, data) {
  return fetchJSON(`/notes/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function getActionItems(params = {}) {
  const query = new URLSearchParams(params).toString();
  return fetchJSON(`/action-items/?${query}`);
}

export function createActionItem(data) {
  return fetchJSON("/action-items/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function completeActionItem(id) {
  return fetchJSON(`/action-items/${id}/complete`, { method: "PUT" });
}

export function patchActionItem(id, data) {
  return fetchJSON(`/action-items/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}
