const BASE = "/api/posts";

export async function fetchPosts(query = "") {
    const url = query ? `${BASE}?q=${encodeURIComponent(query)}` : BASE;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch posts");
    return res.json();
}

export async function fetchPost(id) {
    const res = await fetch(`${BASE}/${id}`);
    if (!res.ok) throw new Error("Post not found");
    return res.json();
}

export async function createPost(data) {
    const res = await fetch(BASE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create post");
    return res.json();
}

export async function updatePost(id, data) {
    const res = await fetch(`${BASE}/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update post");
    return res.json();
}

export async function deletePost(id) {
    const res = await fetch(`${BASE}/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete post");
}
