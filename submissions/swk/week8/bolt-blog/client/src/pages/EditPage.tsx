import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchPost, updatePost } from "../api/client";
import PostForm from "../components/PostForm";
import type { Post, PostInput } from "../types";

export default function EditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [post, setPost] = useState<Post | null>(null);

  useEffect(() => {
    if (id) fetchPost(Number(id)).then(setPost).catch(() => navigate("/"));
  }, [id]);

  const handleSubmit = async (data: PostInput) => {
    if (id) {
      await updatePost(Number(id), data);
      navigate(`/posts/${id}`);
    }
  };

  if (!post) {
    return (
      <div className="text-center py-12">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-violet-200 border-t-violet-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Edit Post</h2>
      <PostForm
        initialData={post}
        onSubmit={handleSubmit}
        submitLabel="Update Post"
      />
    </div>
  );
}
