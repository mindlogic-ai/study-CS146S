import { useState, useEffect } from "react";
import type { PostInput, Post } from "../types";

interface Props {
  initialData?: Post;
  onSubmit: (data: PostInput) => void;
  submitLabel: string;
}

export default function PostForm({ initialData, onSubmit, submitLabel }: Props) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [author, setAuthor] = useState("");
  const [tags, setTags] = useState("");

  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title);
      setContent(initialData.content);
      setAuthor(initialData.author);
      setTags(initialData.tags || "");
    }
  }, [initialData]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ title, content, author, tags });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-1">
          Title
        </label>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={200}
          placeholder="Post title"
          className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition"
        />
      </div>
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-1">
          Author
        </label>
        <input
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          required
          maxLength={100}
          placeholder="Author name"
          className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition"
        />
      </div>
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-1">
          Tags
        </label>
        <input
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="Comma-separated tags (e.g. react, typescript)"
          className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition"
        />
      </div>
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-1">
          Content
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          rows={8}
          placeholder="Write your post..."
          className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition resize-y"
        />
      </div>
      <button
        type="submit"
        className="px-6 py-2.5 bg-violet-600 text-white font-semibold rounded-lg hover:bg-violet-700 transition-colors shadow-sm"
      >
        {submitLabel}
      </button>
    </form>
  );
}
