import { Router } from "express";
import Post from "../models/Post.js";

const router = Router();

// List posts (with optional search)
router.get("/", async (req, res, next) => {
    try {
        const { q } = req.query;
        const filter = q ? { $text: { $search: q } } : {};
        const posts = await Post.find(filter).sort({ createdAt: -1 });
        res.json(posts);
    } catch (err) {
        next(err);
    }
});

// Get single post
router.get("/:id", async (req, res, next) => {
    try {
        const post = await Post.findById(req.params.id);
        if (!post) return res.status(404).json({ error: "Post not found" });
        res.json(post);
    } catch (err) {
        next(err);
    }
});

// Create post
router.post("/", async (req, res, next) => {
    try {
        const { title, content, author, tags } = req.body;
        if (!title || !content || !author) {
            return res.status(400).json({ error: "title, content, and author are required" });
        }
        const post = await Post.create({
            title,
            content,
            author,
            tags: Array.isArray(tags) ? tags : tags ? tags.split(",").map((t) => t.trim()) : [],
        });
        res.status(201).json(post);
    } catch (err) {
        next(err);
    }
});

// Update post
router.put("/:id", async (req, res, next) => {
    try {
        const { title, content, author, tags } = req.body;
        const update = { title, content, author };
        if (tags !== undefined) {
            update.tags = Array.isArray(tags) ? tags : tags.split(",").map((t) => t.trim());
        }
        const post = await Post.findByIdAndUpdate(req.params.id, update, {
            new: true,
            runValidators: true,
        });
        if (!post) return res.status(404).json({ error: "Post not found" });
        res.json(post);
    } catch (err) {
        next(err);
    }
});

// Delete post
router.delete("/:id", async (req, res, next) => {
    try {
        const post = await Post.findByIdAndDelete(req.params.id);
        if (!post) return res.status(404).json({ error: "Post not found" });
        res.status(204).send();
    } catch (err) {
        next(err);
    }
});

export default router;
