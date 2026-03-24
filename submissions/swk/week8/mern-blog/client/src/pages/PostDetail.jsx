import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { fetchPost, deletePost } from "../api/posts";

export default function PostDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [post, setPost] = useState(null);

    useEffect(() => {
        fetchPost(id).then(setPost).catch(() => navigate("/"));
    }, [id]);

    if (!post) return <p>Loading...</p>;

    const handleDelete = async () => {
        if (!confirm("Delete this post?")) return;
        await deletePost(id);
        navigate("/");
    };

    return (
        <div className="post-detail">
            <Link to="/" className="back-link">&larr; Back to posts</Link>
            <h2>{post.title}</h2>
            <div className="post-meta">
                By {post.author} &middot;{" "}
                {new Date(post.createdAt).toLocaleDateString()}
            </div>
            {post.tags?.length > 0 && (
                <div className="post-tags">
                    {post.tags.map((tag, i) => (
                        <span key={i} className="tag">{tag}</span>
                    ))}
                </div>
            )}
            <div className="post-content">{post.content}</div>
            <div className="post-actions">
                <Link to={`/posts/${id}/edit`} className="btn btn-edit">Edit</Link>
                <button className="btn btn-delete" onClick={handleDelete}>Delete</button>
            </div>
        </div>
    );
}
