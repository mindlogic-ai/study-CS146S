import { Link } from "react-router-dom";

export default function PostCard({ post, onDelete }) {
    return (
        <div className="post-card">
            <h3>
                <Link to={`/posts/${post._id}`}>{post.title}</Link>
            </h3>
            <div className="post-meta">
                By {post.author} &middot;{" "}
                {new Date(post.createdAt).toLocaleDateString()}
            </div>
            {post.tags?.length > 0 && (
                <div className="post-tags">
                    {post.tags.map((tag, i) => (
                        <span key={i} className="tag">
                            {tag}
                        </span>
                    ))}
                </div>
            )}
            <p className="post-excerpt">
                {post.content.length > 150
                    ? post.content.slice(0, 150) + "..."
                    : post.content}
            </p>
            <div className="post-actions">
                <Link to={`/posts/${post._id}/edit`} className="btn btn-edit">
                    Edit
                </Link>
                <button className="btn btn-delete" onClick={() => onDelete(post._id)}>
                    Delete
                </button>
            </div>
        </div>
    );
}
