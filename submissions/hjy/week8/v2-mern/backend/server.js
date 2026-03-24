import "dotenv/config";
import express from "express";
import cors from "cors";
import mongoose from "mongoose";
import notesRouter from "./routes/notes.js";
import actionItemsRouter from "./routes/actionItems.js";

const app = express();
const PORT = process.env.PORT || 3001;
const MONGODB_URI =
  process.env.MONGODB_URI || "mongodb://localhost:27017/notesapp";

app.use(cors());
app.use(express.json());

app.use("/api/notes", notesRouter);
app.use("/api/action-items", actionItemsRouter);

app.get("/api/health", (_req, res) => {
  res.json({ status: "ok" });
});

mongoose
  .connect(MONGODB_URI)
  .then(() => {
    console.log("Connected to MongoDB");
    app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error("MongoDB connection error:", err);
    process.exit(1);
  });
