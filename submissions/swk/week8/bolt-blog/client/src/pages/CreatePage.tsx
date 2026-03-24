import { useNavigate } from "react-router-dom";
import { createPost } from "../api/client";
import PostForm from "../components/PostForm";
import type { PostInput } from "../types";

export default function CreatePage() {
  const navigate = useNavigate();

  const handleSubmit = async (data: PostInput) => {
    await createPost(data);
    navigate("/");
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Create New Post
      </h2>
      <PostForm onSubmit={handleSubmit} submitLabel="Create Post" />
    </div>
  );
}
