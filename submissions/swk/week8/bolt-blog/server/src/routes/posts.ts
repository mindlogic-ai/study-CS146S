import { Router, Request, Response } from "express";
import db from "../db.js";
import type { Post, CreatePostBody } from "../types.js";

const router = Router();

// List posts
router.get("/", (req: Request, res: Response) => {
  const { q } = req.query;
  let posts: Post[];
  if (q && typeof q === "string") {
    const pattern = `%${q}%`;
    posts = db
      .prepare(
        `SELECT * FROM posts WHERE title LIKE ? OR content LIKE ? OR author LIKE ? OR tags LIKE ? ORDER BY created_at DESC`
      )
      .all(pattern, pattern, pattern, pattern) as Post[];
  } else {
    posts = db.prepare("SELECT * FROM posts ORDER BY created_at DESC").all() as Post[];
  }
  res.json(posts);
});

// Get single post
router.get("/:id", (req: Request, res: Response) => {
  const post = db.prepare("SELECT * FROM posts WHERE id = ?").get(req.params.id) as Post | undefined;
  if (!post) {
    res.status(404).json({ error: "Post not found" });
    return;
  }
  res.json(post);
});

// Create post
router.post("/", (req: Request, res: Response) => {
  const { title, content, author, tags } = req.body as CreatePostBody;
  if (!title || !content || !author) {
    res.status(400).json({ error: "title, content, and author are required" });
    return;
  }
  const result = db
    .prepare("INSERT INTO posts (title, content, author, tags) VALUES (?, ?, ?, ?)")
    .run(title, content, author, tags || "");
  const post = db.prepare("SELECT * FROM posts WHERE id = ?").get(result.lastInsertRowid) as Post;
  res.status(201).json(post);
});

// Update post
router.put("/:id", (req: Request, res: Response) => {
  const existing = db.prepare("SELECT * FROM posts WHERE id = ?").get(req.params.id) as Post | undefined;
  if (!existing) {
    res.status(404).json({ error: "Post not found" });
    return;
  }
  const { title, content, author, tags } = req.body as CreatePostBody;
  db.prepare(
    "UPDATE posts SET title = ?, content = ?, author = ?, tags = ?, updated_at = datetime('now') WHERE id = ?"
  ).run(title || existing.title, content || existing.content, author || existing.author, tags ?? existing.tags, req.params.id);
  const post = db.prepare("SELECT * FROM posts WHERE id = ?").get(req.params.id) as Post;
  res.json(post);
});

// Delete post
router.delete("/:id", (req: Request, res: Response) => {
  const existing = db.prepare("SELECT * FROM posts WHERE id = ?").get(req.params.id) as Post | undefined;
  if (!existing) {
    res.status(404).json({ error: "Post not found" });
    return;
  }
  db.prepare("DELETE FROM posts WHERE id = ?").run(req.params.id);
  res.status(204).send();
});

export default router;
