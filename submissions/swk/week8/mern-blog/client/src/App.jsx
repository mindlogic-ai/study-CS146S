import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import PostList from "./pages/PostList";
import PostDetail from "./pages/PostDetail";
import PostCreate from "./pages/PostCreate";
import PostEdit from "./pages/PostEdit";
import "./App.css";

function App() {
    return (
        <BrowserRouter>
            <header>
                <Link to="/" className="header-link">
                    <h1>MERN Blog</h1>
                </Link>
                <p>Built with MongoDB, Express, React, Node.js</p>
            </header>
            <main>
                <Routes>
                    <Route path="/" element={<PostList />} />
                    <Route path="/posts/new" element={<PostCreate />} />
                    <Route path="/posts/:id" element={<PostDetail />} />
                    <Route path="/posts/:id/edit" element={<PostEdit />} />
                </Routes>
            </main>
        </BrowserRouter>
    );
}

export default App;
