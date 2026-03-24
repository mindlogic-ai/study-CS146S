import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { fetchPost, deletePost } from "../api/client";
import type { Post } from "../types";

export default function PostPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [post, setPost] = useState<Post | null>(null);

  useEffect(() => {
    if (id) fetchPost(Number(id)).then(setPost).catch(() => navigate("/"));
  }, [id]);

  if (!post) {
    return (
      <div className="text-center py-12">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-violet-200 border-t-violet-600"></div>
      </div>
    );
  }

  const handleDelete = async () => {
    if (!confirm("Delete this post?")) return;
    await deletePost(post.id);
    navigate("/");
  };

  const tags = post.tags ? post.tags.split(",").filter((t) => t.trim()) : [];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
      <Link
        to="/"
        className="text-violet-600 hover:text-violet-800 text-sm font-medium no-underline"
      >
        &larr; Back to posts
      </Link>

      <h2 className="text-3xl font-bold text-gray-900 mt-4">{post.title}</h2>

      <p className="text-gray-500 mt-2">
        By {post.author} &middot;{" "}
        {new Date(post.created_at).toLocaleDateString()}
      </p>

      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {tags.map((tag, i) => (
            <span
              key={i}
              className="bg-violet-50 text-violet-700 text-xs font-medium px-2.5 py-0.5 rounded-full"
            >
              {tag.trim()}
            </span>
          ))}
        </div>
      )}

      <div className="mt-6 text-gray-700 whitespace-pre-wrap leading-relaxed">
        {post.content}
      </div>

      <div className="flex gap-3 mt-8 pt-6 border-t border-gray-100">
        <Link
          to={`/posts/${post.id}/edit`}
          className="px-5 py-2 bg-amber-500 text-white font-medium rounded-lg hover:bg-amber-600 transition-colors no-underline"
        >
          Edit
        </Link>
        <button
          onClick={handleDelete}
          className="px-5 py-2 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
