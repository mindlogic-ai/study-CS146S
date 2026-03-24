const BASE = "/api";

export async function fetchJSON(url, options) {
  const res = await fetch(BASE + url, options);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

export const notesApi = {
  list: (params = {}) => fetchJSON("/notes?" + new URLSearchParams(params)),
  create: (data) =>
    fetchJSON("/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
  update: (id, data) =>
    fetchJSON(`/notes/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
  delete: (id) => fetchJSON(`/notes/${id}`, { method: "DELETE" }),
};

export const actionItemsApi = {
  list: (params = {}) =>
    fetchJSON("/action-items?" + new URLSearchParams(params)),
  create: (data) =>
    fetchJSON("/action-items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
  complete: (id) =>
    fetchJSON(`/action-items/${id}/complete`, { method: "PUT" }),
  update: (id, data) =>
    fetchJSON(`/action-items/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
  delete: (id) => fetchJSON(`/action-items/${id}`, { method: "DELETE" }),
};
