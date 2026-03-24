require("dotenv").config();
const mongoose = require("mongoose");
const Note = require("./models/Note");
const ActionItem = require("./models/ActionItem");

const MONGODB_URI =
  process.env.MONGODB_URI || "mongodb://localhost:27017/notesapp";

async function seed() {
  await mongoose.connect(MONGODB_URI);
  console.log("Connected to MongoDB");

  await Note.deleteMany({});
  await ActionItem.deleteMany({});

  await Note.create([
    {
      title: "Welcome",
      content: "This is a starter note. TODO: explore the app!",
    },
    { title: "Demo", content: "Click around and add a note. Ship feature!" },
  ]);

  await ActionItem.create([
    { description: "Try pre-commit", completed: false },
    { description: "Run tests", completed: false },
  ]);

  console.log("Seeded 2 notes and 2 action items");
  await mongoose.disconnect();
}

seed().catch(console.error);
