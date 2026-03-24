const express = require("express");
const Note = require("../models/Note");

const router = express.Router();

// GET /api/notes - list with search, pagination, sort
router.get("/", async (req, res) => {
  try {
    const { q, skip = 0, limit = 50, sort = "-createdAt" } = req.query;

    const filter = {};
    if (q) {
      const regex = new RegExp(q, "i");
      filter.$or = [{ title: regex }, { content: regex }];
    }

    const sortField = sort.startsWith("-") ? sort.slice(1) : sort;
    const sortOrder = sort.startsWith("-") ? -1 : 1;
    const sortObj = { [sortField]: sortOrder };

    const notes = await Note.find(filter)
      .sort(sortObj)
      .skip(Number(skip))
      .limit(Number(limit));

    res.json(notes);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// POST /api/notes - create
router.post("/", async (req, res) => {
  try {
    const note = await Note.create(req.body);
    res.status(201).json(note);
  } catch (err) {
    res.status(400).json({ detail: err.message });
  }
});

// GET /api/notes/:id
router.get("/:id", async (req, res) => {
  try {
    const note = await Note.findById(req.params.id);
    if (!note) return res.status(404).json({ detail: "Note not found" });
    res.json(note);
  } catch (err) {
    res.status(500).json({ detail: err.message });
  }
});

// PATCH /api/notes/:id - partial update
router.patch("/:id", async (req, res) => {
  try {
    const note = await Note.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true,
    });
    if (!note) return res.status(404).json({ detail: "Note not found" });
    res.json(note);
  } catch (err) {
    res.status(400).json({ detail: err.message });
  }
});

module.exports = router;
