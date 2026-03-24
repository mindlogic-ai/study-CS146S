import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchPosts, deletePost } from "../api/posts";
import PostCard from "../components/PostCard";

export default function PostList() {
    const [posts, setPosts] = useState([]);
    const [search, setSearch] = useState("");

    const load = async () => {
        const data = await fetchPosts(search);
        setPosts(data);
    };

    useEffect(() => {
        load();
    }, [search]);

    const handleDelete = async (id) => {
        if (!confirm("Delete this post?")) return;
        await deletePost(id);
        load();
    };

    return (
        <div>
            <div className="list-header">
                <h2>All Posts</h2>
                <Link to="/posts/new" className="btn btn-primary">
                    + New Post
                </Link>
            </div>
            <input
                className="search-input"
                placeholder="Search posts..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
            />
            {posts.length === 0 ? (
                <p className="empty">No posts found.</p>
            ) : (
                posts.map((p) => (
                    <PostCard key={p._id} post={p} onDelete={handleDelete} />
                ))
            )}
        </div>
    );
}
