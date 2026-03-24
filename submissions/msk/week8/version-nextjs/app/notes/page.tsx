"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Trash2, Plus, ArrowLeft } from "lucide-react";
import Link from "next/link";

interface Note {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editData, setEditData] = useState({ title: "", content: "" });
  const [newNote, setNewNote] = useState({ title: "", content: "" });
  const searchParams = useSearchParams();
  const q = searchParams.get("q") || "";

  useEffect(() => {
    fetchNotes();
  }, [q]);

  const fetchNotes = async () => {
    try {
      setLoading(true);
      const url = q ? `/api/notes?q=${encodeURIComponent(q)}` : "/api/notes";
      const response = await fetch(url);
      const data = await response.json();
      setNotes(data);
    } catch (error) {
      console.error("Failed to fetch notes:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newNote.title.trim() || !newNote.content.trim()) return;

    try {
      const response = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newNote),
      });

      if (response.ok) {
        const created = await response.json();
        setNotes([created, ...notes]);
        setNewNote({ title: "", content: "" });
      }
    } catch (error) {
      console.error("Failed to create note:", error);
    }
  };

  const handleEdit = async (id: string) => {
    if (!editData.title.trim() || !editData.content.trim()) return;

    try {
      const response = await fetch(`/api/notes/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editData),
      });

      if (response.ok) {
        const updated = await response.json();
        setNotes(notes.map((note) => (note.id === id ? updated : note)));
        setEditingId(null);
      }
    } catch (error) {
      console.error("Failed to update note:", error);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`/api/notes/${id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        setNotes(notes.filter((note) => note.id !== id));
      }
    } catch (error) {
      console.error("Failed to delete note:", error);
    }
  };

  const startEdit = (note: Note) => {
    setEditingId(note.id);
    setEditData({ title: note.title, content: note.content });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <h1 className="text-4xl font-bold text-slate-900">Notes</h1>
        </div>

        <div className="mb-8">
          <Input
            type="text"
            placeholder="Search notes by title or content..."
            defaultValue={q}
            onChange={(e) => {
              const params = new URLSearchParams();
              if (e.target.value) {
                params.set("q", e.target.value);
              }
              window.history.replaceState(
                {},
                "",
                `/notes${params.toString() ? "?" + params.toString() : ""}`
              );
              fetchNotes();
            }}
            className="w-full"
          />
        </div>

        <Card className="mb-8 border-0 shadow-md">
          <CardHeader>
            <CardTitle className="text-lg">Create New Note</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Note title..."
              value={newNote.title}
              onChange={(e) =>
                setNewNote({ ...newNote, title: e.target.value })
              }
            />
            <Textarea
              placeholder="Note content..."
              value={newNote.content}
              onChange={(e) =>
                setNewNote({ ...newNote, content: e.target.value })
              }
              className="min-h-32"
            />
            <Button onClick={handleCreate} className="w-full">
              <Plus className="w-4 h-4 mr-2" />
              Create Note
            </Button>
          </CardContent>
        </Card>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-slate-600">Loading notes...</p>
          </div>
        ) : notes.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-600">
              {q ? "No notes found matching your search." : "No notes yet. Create one to get started!"}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {notes.map((note) => (
              <Card key={note.id} className="border-0 shadow-md hover:shadow-lg transition-shadow">
                {editingId === note.id ? (
                  <CardContent className="pt-6 space-y-4">
                    <Input
                      value={editData.title}
                      onChange={(e) =>
                        setEditData({ ...editData, title: e.target.value })
                      }
                      placeholder="Note title..."
                    />
                    <Textarea
                      value={editData.content}
                      onChange={(e) =>
                        setEditData({ ...editData, content: e.target.value })
                      }
                      placeholder="Note content..."
                      className="min-h-32"
                    />
                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleEdit(note.id)}
                        className="flex-1"
                      >
                        Save Changes
                      </Button>
                      <Button
                        onClick={() => setEditingId(null)}
                        variant="outline"
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                    </div>
                  </CardContent>
                ) : (
                  <CardContent className="pt-6">
                    <h2 className="text-xl font-semibold text-slate-900 mb-2 cursor-pointer hover:text-blue-600"
                        onClick={() => startEdit(note)}>
                      {note.title}
                    </h2>
                    <p className="text-slate-700 mb-4 cursor-pointer hover:text-slate-900 whitespace-pre-wrap"
                       onClick={() => startEdit(note)}>
                      {note.content}
                    </p>
                    <div className="flex justify-between items-center text-sm text-slate-500">
                      <span>
                        Updated{" "}
                        {new Date(note.updated_at).toLocaleDateString(
                          "en-US",
                          {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          }
                        )}
                      </span>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => startEdit(note)}
                          variant="outline"
                          size="sm"
                        >
                          Edit
                        </Button>
                        <Button
                          onClick={() => handleDelete(note.id)}
                          variant="destructive"
                          size="sm"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

