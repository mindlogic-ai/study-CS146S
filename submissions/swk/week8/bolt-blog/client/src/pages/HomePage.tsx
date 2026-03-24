import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchPosts, deletePost } from "../api/client";
import PostCard from "../components/PostCard";
import type { Post } from "../types";

export default function HomePage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchPosts(search);
      setPosts(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [search]);

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this post?")) return;
    await deletePost(id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">All Posts</h2>
        <Link
          to="/posts/new"
          className="px-5 py-2.5 bg-violet-600 text-white font-semibold rounded-lg hover:bg-violet-700 transition-colors shadow-sm no-underline"
        >
          + New Post
        </Link>
      </div>

      <input
        type="text"
        placeholder="Search posts..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-4 py-3 border border-gray-200 rounded-lg mb-6 focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition"
      />

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-violet-200 border-t-violet-600"></div>
          <p className="text-gray-500 mt-3">Loading posts...</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg">No posts found.</p>
          <p className="mt-1">Create your first post to get started!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
}
