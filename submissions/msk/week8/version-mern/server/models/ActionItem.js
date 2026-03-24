const mongoose = require("mongoose");

const actionItemSchema = new mongoose.Schema(
  {
    description: { type: String, required: true },
    completed: { type: Boolean, default: false },
  },
  { timestamps: true }
);

module.exports = mongoose.model("ActionItem", actionItemSchema);
