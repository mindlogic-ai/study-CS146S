import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchPost, updatePost } from "../api/posts";
import PostForm from "../components/PostForm";

export default function PostEdit() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [post, setPost] = useState(null);

    useEffect(() => {
        fetchPost(id).then(setPost).catch(() => navigate("/"));
    }, [id]);

    const handleSubmit = async (data) => {
        await updatePost(id, data);
        navigate(`/posts/${id}`);
    };

    if (!post) return <p>Loading...</p>;

    return (
        <div>
            <h2>Edit Post</h2>
            <PostForm initialData={post} onSubmit={handleSubmit} submitLabel="Update Post" />
        </div>
    );
}
