import mongoose from "mongoose";

const postSchema = new mongoose.Schema(
    {
        title: { type: String, required: true, maxlength: 200 },
        content: { type: String, required: true },
        author: { type: String, required: true, maxlength: 100 },
        tags: [String],
    },
    { timestamps: true }
);

postSchema.index({ title: "text", content: "text", author: "text" });

export default mongoose.model("Post", postSchema);
