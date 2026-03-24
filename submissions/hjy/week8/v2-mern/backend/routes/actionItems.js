import { Router } from "express";
import ActionItem from "../models/ActionItem.js";

const router = Router();

// GET /api/action-items - list items with optional completed filter
router.get("/", async (req, res) => {
  try {
    const { completed } = req.query;
    let filter = {};
    if (completed !== undefined) {
      filter.completed = completed === "true";
    }
    const items = await ActionItem.find(filter).sort({ createdAt: -1 });
    res.json(items);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/action-items - create item
router.post("/", async (req, res) => {
  try {
    const item = await ActionItem.create(req.body);
    res.status(201).json(item);
  } catch (err) {
    if (err.name === "ValidationError") {
      return res.status(422).json({ error: err.message });
    }
    res.status(500).json({ error: err.message });
  }
});

// PATCH /api/action-items/:id - partial update (including complete/reopen toggle)
router.patch("/:id", async (req, res) => {
  try {
    const item = await ActionItem.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true,
    });
    if (!item) return res.status(404).json({ error: "Action item not found" });
    res.json(item);
  } catch (err) {
    if (err.name === "ValidationError") {
      return res.status(422).json({ error: err.message });
    }
    res.status(500).json({ error: err.message });
  }
});

// DELETE /api/action-items/:id - delete item
router.delete("/:id", async (req, res) => {
  try {
    const item = await ActionItem.findByIdAndDelete(req.params.id);
    if (!item)
      return res.status(404).json({ error: "Action item not found" });
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
