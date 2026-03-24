const express = require("express");
const ActionItem = require("../models/ActionItem");

const router = express.Router();

// GET /api/action-items - list with filter, pagination, sort
router.get("/", async (req, res) => {
  try {
    const { completed, skip = 0, limit = 50, sort = "-createdAt" } = req.query;

    const filter = {};
    if (completed !== undefined) {
      filter.completed = completed === "true";
    }

    const sortField = sort.startsWith("-") ? sort.slice(1) : sort;
    const sortOrder = sort.startsWith("-") ? -1 : 1;
    const sortObj = { [sortField]: sortOrder };

    const items = await ActionItem.find(filter)
      .sort(sortObj)
      .skip(Number(skip))
      .limit(Number(limit));

    res.json(items);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// POST /api/action-items - create
router.post("/", async (req, res) => {
  try {
    const item = await ActionItem.create({
      description: req.body.description,
      completed: false,
    });
    res.status(201).json(item);
  } catch (err) {
    res.status(400).json({ detail: err.message });
  }
});

// GET /api/action-items/:id
router.get("/:id", async (req, res) => {
  try {
    const item = await ActionItem.findById(req.params.id);
    if (!item) return res.status(404).json({ detail: "Action item not found" });
    res.json(item);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// PUT /api/action-items/:id/complete - mark complete
router.put("/:id/complete", async (req, res) => {
  try {
    const item = await ActionItem.findByIdAndUpdate(
      req.params.id,
      { completed: true },
      { new: true }
    );
    if (!item) return res.status(404).json({ detail: "Action item not found" });
    res.json(item);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// PATCH /api/action-items/:id - partial update
router.patch("/:id", async (req, res) => {
  try {
    const item = await ActionItem.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true,
    });
    if (!item) return res.status(404).json({ detail: "Action item not found" });
    res.json(item);
  } catch (err) {
    res.status(400).json({ detail: err.message });
  }
});

module.exports = router;
