const API_URL = "/api/posts/";
let editingId = null;

document.getElementById("post-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        title: document.getElementById("title").value,
        content: document.getElementById("content").value,
        author: document.getElementById("author").value,
        tags: document.getElementById("tags").value,
    };

    try {
        if (editingId) {
            await fetch(`${API_URL}${editingId}/`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });
        } else {
            await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });
        }
        resetForm();
        loadPosts();
    } catch (err) {
        alert("Error saving post: " + err.message);
    }
});

async function loadPosts(query = "") {
    const url = query ? `${API_URL}?search=${encodeURIComponent(query)}` : API_URL;
    const res = await fetch(url);
    const posts = await res.json();
    const container = document.getElementById("posts-container");

    if (posts.length === 0) {
        container.innerHTML = '<div class="empty-state">No posts yet. Create one above!</div>';
        return;
    }

    container.innerHTML = posts
        .map(
            (post) => `
        <div class="post-card">
            <h3>${escapeHtml(post.title)}</h3>
            <div class="post-meta">
                By ${escapeHtml(post.author)} &middot; ${new Date(post.created_at).toLocaleDateString()}
            </div>
            ${
                post.tags
                    ? `<div class="post-tags">${post.tags
                          .split(",")
                          .map((t) => `<span class="tag">${escapeHtml(t.trim())}</span>`)
                          .join("")}</div>`
                    : ""
            }
            <div class="post-content">${escapeHtml(post.content)}</div>
            <div class="post-actions">
                <button class="btn-edit" onclick="editPost(${post.id})">Edit</button>
                <button class="btn-delete" onclick="deletePost(${post.id})">Delete</button>
            </div>
        </div>
    `
        )
        .join("");
}

async function editPost(id) {
    const res = await fetch(`${API_URL}${id}/`);
    const post = await res.json();

    document.getElementById("post-id").value = post.id;
    document.getElementById("title").value = post.title;
    document.getElementById("content").value = post.content;
    document.getElementById("author").value = post.author;
    document.getElementById("tags").value = post.tags || "";

    editingId = post.id;
    document.getElementById("form-title").textContent = "Edit Post";
    document.getElementById("submit-btn").textContent = "Update Post";
    document.getElementById("cancel-btn").style.display = "inline-block";
    window.scrollTo({ top: 0, behavior: "smooth" });
}

async function deletePost(id) {
    if (!confirm("Are you sure you want to delete this post?")) return;
    await fetch(`${API_URL}${id}/`, { method: "DELETE" });
    loadPosts();
}

function resetForm() {
    editingId = null;
    document.getElementById("post-form").reset();
    document.getElementById("post-id").value = "";
    document.getElementById("form-title").textContent = "Create New Post";
    document.getElementById("submit-btn").textContent = "Create Post";
    document.getElementById("cancel-btn").style.display = "none";
}

function searchPosts() {
    const query = document.getElementById("search-input").value;
    loadPosts(query);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Initial load
loadPosts();
