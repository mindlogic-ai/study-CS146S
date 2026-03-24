import express from "express";
import cors from "cors";
import postsRouter from "./routes/posts.js";

const app = express();
const PORT = process.env.PORT || 5001;

app.use(cors());
app.use(express.json());
app.use("/api/posts", postsRouter);

app.listen(PORT, () => {
  console.log(`Bolt Blog server running on http://localhost:${PORT}`);
});
