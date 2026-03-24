import { Link, Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <Link to="/" className="text-white no-underline">
            <h1 className="text-3xl font-bold tracking-tight">Bolt Blog</h1>
          </Link>
          <p className="text-violet-200 mt-1">
            Built with React + TypeScript + Tailwind CSS
          </p>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
