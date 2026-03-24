import { useNavigate } from "react-router-dom";
import { createPost } from "../api/posts";
import PostForm from "../components/PostForm";

export default function PostCreate() {
    const navigate = useNavigate();

    const handleSubmit = async (data) => {
        await createPost(data);
        navigate("/");
    };

    return (
        <div>
            <h2>Create New Post</h2>
            <PostForm onSubmit={handleSubmit} submitLabel="Create Post" />
        </div>
    );
}
