import express from "express";
import cors from "cors";
import notesRouter from "./routes/notes.js";
import actionItemsRouter from "./routes/actionItems.js";

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

app.use("/api/notes", notesRouter);
app.use("/api/action-items", actionItemsRouter);

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
