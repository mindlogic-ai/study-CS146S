import { useState, useEffect } from "react";

export default function PostForm({ initialData, onSubmit, submitLabel }) {
    const [title, setTitle] = useState("");
    const [content, setContent] = useState("");
    const [author, setAuthor] = useState("");
    const [tags, setTags] = useState("");

    useEffect(() => {
        if (initialData) {
            setTitle(initialData.title || "");
            setContent(initialData.content || "");
            setAuthor(initialData.author || "");
            setTags(initialData.tags?.join(", ") || "");
        }
    }, [initialData]);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({ title, content, author, tags });
    };

    return (
        <form onSubmit={handleSubmit} className="post-form">
            <div className="form-group">
                <label>Title</label>
                <input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                    maxLength={200}
                    placeholder="Post title"
                />
            </div>
            <div className="form-group">
                <label>Author</label>
                <input
                    value={author}
                    onChange={(e) => setAuthor(e.target.value)}
                    required
                    maxLength={100}
                    placeholder="Author name"
                />
            </div>
            <div className="form-group">
                <label>Tags</label>
                <input
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="Comma-separated tags"
                />
            </div>
            <div className="form-group">
                <label>Content</label>
                <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    required
                    rows={8}
                    placeholder="Write your post..."
                />
            </div>
            <button type="submit" className="btn btn-primary">
                {submitLabel || "Submit"}
            </button>
        </form>
    );
}
