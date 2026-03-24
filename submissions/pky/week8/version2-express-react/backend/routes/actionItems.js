import { Router } from "express";
import db from "../db.js";

const router = Router();

router.get("/", (req, res) => {
  const { completed, skip = 0, limit = 20, sort = "-created_at" } = req.query;

  const desc = sort.startsWith("-");
  const field = desc ? sort.slice(1) : sort;
  const allowed = ["id", "description", "completed", "created_at", "updated_at"];
  const orderField = allowed.includes(field) ? field : "created_at";
  const orderDir = desc ? "DESC" : "ASC";

  let sql = "SELECT * FROM action_items";
  const params = [];

  if (completed !== undefined) {
    sql += " WHERE completed = ?";
    params.push(completed === "true" ? 1 : 0);
  }

  sql += ` ORDER BY ${orderField} ${orderDir} LIMIT ? OFFSET ?`;
  params.push(Number(limit), Number(skip));

  const rows = db.prepare(sql).all(...params);
  res.json(rows);
});

router.post("/", (req, res) => {
  const { description } = req.body;
  if (!description) {
    return res.status(400).json({ error: "description is required" });
  }
  const result = db
    .prepare("INSERT INTO action_items (description) VALUES (?)")
    .run(description);
  const item = db
    .prepare("SELECT * FROM action_items WHERE id = ?")
    .get(result.lastInsertRowid);
  res.status(201).json(item);
});

router.patch("/:id", (req, res) => {
  const item = db
    .prepare("SELECT * FROM action_items WHERE id = ?")
    .get(req.params.id);
  if (!item) return res.status(404).json({ error: "Action item not found" });

  const updates = [];
  const params = [];

  if (req.body.description !== undefined) {
    updates.push("description = ?");
    params.push(req.body.description);
  }
  if (req.body.completed !== undefined) {
    updates.push("completed = ?");
    params.push(req.body.completed ? 1 : 0);
  }

  if (updates.length === 0) {
    return res.json(item);
  }

  updates.push("updated_at = CURRENT_TIMESTAMP");
  params.push(req.params.id);

  db.prepare(`UPDATE action_items SET ${updates.join(", ")} WHERE id = ?`).run(
    ...params
  );
  const updated = db
    .prepare("SELECT * FROM action_items WHERE id = ?")
    .get(req.params.id);
  res.json(updated);
});

router.put("/:id/complete", (req, res) => {
  const item = db
    .prepare("SELECT * FROM action_items WHERE id = ?")
    .get(req.params.id);
  if (!item) return res.status(404).json({ error: "Action item not found" });

  db.prepare(
    "UPDATE action_items SET completed = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
  ).run(req.params.id);
  const updated = db
    .prepare("SELECT * FROM action_items WHERE id = ?")
    .get(req.params.id);
  res.json(updated);
});

router.delete("/:id", (req, res) => {
  const item = db.prepare("SELECT * FROM action_items WHERE id = ?").get(req.params.id);
  if (!item) return res.status(404).json({ error: "Action item not found" });
  db.prepare("DELETE FROM action_items WHERE id = ?").run(req.params.id);
  res.status(204).end();
});

export default router;
