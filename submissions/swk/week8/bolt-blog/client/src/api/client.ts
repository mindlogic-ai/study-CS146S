import type { Post, PostInput } from "../types";

const BASE = "/api/posts";

export async function fetchPosts(query = ""): Promise<Post[]> {
  const url = query ? `${BASE}?q=${encodeURIComponent(query)}` : BASE;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch posts");
  return res.json();
}

export async function fetchPost(id: number): Promise<Post> {
  const res = await fetch(`${BASE}/${id}`);
  if (!res.ok) throw new Error("Post not found");
  return res.json();
}

export async function createPost(data: PostInput): Promise<Post> {
  const res = await fetch(BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create post");
  return res.json();
}

export async function updatePost(id: number, data: PostInput): Promise<Post> {
  const res = await fetch(`${BASE}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update post");
  return res.json();
}

export async function deletePost(id: number): Promise<void> {
  const res = await fetch(`${BASE}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete post");
}
