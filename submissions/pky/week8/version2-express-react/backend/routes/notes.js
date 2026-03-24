import { Router } from "express";
import db from "../db.js";

const router = Router();

router.get("/", (req, res) => {
  const { q, skip = 0, limit = 20, sort = "-created_at" } = req.query;

  const desc = sort.startsWith("-");
  const field = desc ? sort.slice(1) : sort;
  const allowed = ["id", "title", "created_at", "updated_at"];
  const orderField = allowed.includes(field) ? field : "created_at";
  const orderDir = desc ? "DESC" : "ASC";

  let sql = "SELECT * FROM notes";
  const params = [];

  if (q) {
    sql += " WHERE title LIKE ? OR content LIKE ?";
    params.push(`%${q}%`, `%${q}%`);
  }

  sql += ` ORDER BY ${orderField} ${orderDir} LIMIT ? OFFSET ?`;
  params.push(Number(limit), Number(skip));

  const rows = db.prepare(sql).all(...params);
  res.json(rows);
});

router.post("/", (req, res) => {
  const { title, content } = req.body;
  if (!title || !content) {
    return res.status(400).json({ error: "title and content are required" });
  }
  const result = db.prepare("INSERT INTO notes (title, content) VALUES (?, ?)").run(title, content);
  const note = db.prepare("SELECT * FROM notes WHERE id = ?").get(result.lastInsertRowid);
  res.status(201).json(note);
});

router.get("/:id", (req, res) => {
  const note = db.prepare("SELECT * FROM notes WHERE id = ?").get(req.params.id);
  if (!note) return res.status(404).json({ error: "Note not found" });
  res.json(note);
});

router.patch("/:id", (req, res) => {
  const note = db.prepare("SELECT * FROM notes WHERE id = ?").get(req.params.id);
  if (!note) return res.status(404).json({ error: "Note not found" });

  const updates = [];
  const params = [];

  if (req.body.title !== undefined) {
    updates.push("title = ?");
    params.push(req.body.title);
  }
  if (req.body.content !== undefined) {
    updates.push("content = ?");
    params.push(req.body.content);
  }

  if (updates.length === 0) {
    return res.json(note);
  }

  updates.push("updated_at = CURRENT_TIMESTAMP");
  params.push(req.params.id);

  db.prepare(`UPDATE notes SET ${updates.join(", ")} WHERE id = ?`).run(...params);
  const updated = db.prepare("SELECT * FROM notes WHERE id = ?").get(req.params.id);
  res.json(updated);
});

router.delete("/:id", (req, res) => {
  const note = db.prepare("SELECT * FROM notes WHERE id = ?").get(req.params.id);
  if (!note) return res.status(404).json({ error: "Note not found" });
  db.prepare("DELETE FROM notes WHERE id = ?").run(req.params.id);
  res.status(204).end();
});

export default router;
