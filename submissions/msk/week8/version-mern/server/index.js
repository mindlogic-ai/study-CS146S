const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const { MongoMemoryServer } = require("mongodb-memory-server");
const notesRouter = require("./routes/notes");
const actionItemsRouter = require("./routes/actionItems");

const app = express();
const PORT = process.env.PORT || 5001;

app.use(cors());
app.use(express.json());

app.use("/api/notes", notesRouter);
app.use("/api/action-items", actionItemsRouter);

app.get("/api/health", (_req, res) => res.json({ status: "ok" }));

async function start() {
  const mongod = await MongoMemoryServer.create();
  const uri = mongod.getUri();
  await mongoose.connect(uri);
  console.log("Connected to in-memory MongoDB");

  app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

start().catch(console.error);
