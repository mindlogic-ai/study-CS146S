import { Link } from "react-router-dom";
import type { Post } from "../types";

interface Props {
  post: Post;
  onDelete: (id: number) => void;
}

export default function PostCard({ post, onDelete }: Props) {
  const tags = post.tags
    ? post.tags.split(",").filter((t) => t.trim())
    : [];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
      <Link to={`/posts/${post.id}`} className="no-underline">
        <h3 className="text-xl font-semibold text-gray-900 hover:text-violet-600 transition-colors">
          {post.title}
        </h3>
      </Link>
      <p className="text-sm text-gray-500 mt-1">
        By {post.author} &middot;{" "}
        {new Date(post.created_at).toLocaleDateString()}
      </p>
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
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
      <p className="text-gray-600 mt-3 line-clamp-2">
        {post.content.length > 150
          ? post.content.slice(0, 150) + "..."
          : post.content}
      </p>
      <div className="flex gap-2 mt-4">
        <Link
          to={`/posts/${post.id}/edit`}
          className="px-4 py-1.5 bg-amber-500 text-white text-sm font-medium rounded-lg hover:bg-amber-600 transition-colors no-underline"
        >
          Edit
        </Link>
        <button
          onClick={() => onDelete(post.id)}
          className="px-4 py-1.5 bg-red-500 text-white text-sm font-medium rounded-lg hover:bg-red-600 transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
