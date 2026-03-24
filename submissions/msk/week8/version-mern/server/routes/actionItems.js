const express = require("express");
const ActionItem = require("../models/ActionItem");

const router = express.Router();

router.get("/", async (req, res) => {
  try {
    const { completed } = req.query;
    let query = {};
    if (completed !== undefined) {
      query.completed = completed === "true";
    }
    const items = await ActionItem.find(query).sort({ updatedAt: -1 });
    res.json(items);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const item = await ActionItem.findById(req.params.id);
    if (!item) return res.status(404).json({ error: "Action item not found" });
    res.json(item);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post("/", async (req, res) => {
  try {
    const { description } = req.body;
    if (!description) {
      return res.status(400).json({ error: "Description is required" });
    }
    const item = await ActionItem.create({ description });
    res.status(201).json(item);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.patch("/:id", async (req, res) => {
  try {
    const item = await ActionItem.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true,
    });
    if (!item) return res.status(404).json({ error: "Action item not found" });
    res.json(item);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const item = await ActionItem.findByIdAndDelete(req.params.id);
    if (!item) return res.status(404).json({ error: "Action item not found" });
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
