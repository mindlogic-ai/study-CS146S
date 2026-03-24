const mongoose = require("mongoose");

const noteSchema = new mongoose.Schema(
  {
    title: { type: String, required: true, maxlength: 200 },
    content: { type: String, required: true },
  },
  { timestamps: true }
);

noteSchema.index({ title: "text", content: "text" });

module.exports = mongoose.model("Note", noteSchema);
