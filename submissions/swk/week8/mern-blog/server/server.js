import "dotenv/config";
import express from "express";
import cors from "cors";
import connectDB from "./config/db.js";
import postsRouter from "./routes/posts.js";
import errorHandler from "./middleware/errorHandler.js";

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.use("/api/posts", postsRouter);
app.use(errorHandler);

connectDB().then(() => {
    app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
});
