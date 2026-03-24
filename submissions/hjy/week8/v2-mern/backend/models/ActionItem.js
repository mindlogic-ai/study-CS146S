import mongoose from "mongoose";

const actionItemSchema = new mongoose.Schema(
  {
    description: {
      type: String,
      required: [true, "Description is required"],
      trim: true,
    },
    completed: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: true,
  }
);

const ActionItem = mongoose.model("ActionItem", actionItemSchema);

export default ActionItem;
