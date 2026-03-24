"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Trash2, Plus, ArrowLeft } from "lucide-react";
import Link from "next/link";

interface ActionItem {
  id: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export default function ActionItemsPage() {
  const [items, setItems] = useState<ActionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDescription, setEditDescription] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [showCompleted, setShowCompleted] = useState(false);
  const searchParams = useSearchParams();

  useEffect(() => {
    fetchItems();
  }, [showCompleted]);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const url = showCompleted
        ? "/api/action-items?completed=true"
        : "/api/action-items";
      const response = await fetch(url);
      const data = await response.json();
      setItems(data);
    } catch (error) {
      console.error("Failed to fetch action items:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newDescription.trim()) return;

    try {
      const response = await fetch("/api/action-items", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: newDescription }),
      });

      if (response.ok) {
        const created = await response.json();
        if (!showCompleted || !created.completed) {
          setItems([created, ...items]);
        }
        setNewDescription("");
      }
    } catch (error) {
      console.error("Failed to create action item:", error);
    }
  };

  const handleToggleComplete = async (item: ActionItem) => {
    try {
      const response = await fetch(`/api/action-items/${item.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completed: !item.completed }),
      });

      if (response.ok) {
        const updated = await response.json();
        if (showCompleted && !updated.completed) {
          setItems(items.filter((i) => i.id !== item.id));
        } else {
          setItems(items.map((i) => (i.id === item.id ? updated : i)));
        }
      }
    } catch (error) {
      console.error("Failed to update action item:", error);
    }
  };

  const handleEdit = async (id: string) => {
    if (!editDescription.trim()) return;

    try {
      const response = await fetch(`/api/action-items/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: editDescription }),
      });

      if (response.ok) {
        const updated = await response.json();
        setItems(items.map((item) => (item.id === id ? updated : item)));
        setEditingId(null);
      }
    } catch (error) {
      console.error("Failed to update action item:", error);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`/api/action-items/${id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        setItems(items.filter((item) => item.id !== id));
      }
    } catch (error) {
      console.error("Failed to delete action item:", error);
    }
  };

  const startEdit = (item: ActionItem) => {
    setEditingId(item.id);
    setEditDescription(item.description);
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
          <h1 className="text-4xl font-bold text-slate-900">Action Items</h1>
        </div>

        <div className="flex items-center gap-3 mb-8">
          <Checkbox
            id="show-completed"
            checked={showCompleted}
            onCheckedChange={(checked) => setShowCompleted(checked as boolean)}
          />
          <label
            htmlFor="show-completed"
            className="text-sm font-medium cursor-pointer"
          >
            Show Completed Items
          </label>
        </div>

        <Card className="mb-8 border-0 shadow-md">
          <CardHeader>
            <CardTitle className="text-lg">Create New Action Item</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="What needs to be done?..."
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleCreate();
                }
              }}
            />
            <Button onClick={handleCreate} className="w-full">
              <Plus className="w-4 h-4 mr-2" />
              Create Action Item
            </Button>
          </CardContent>
        </Card>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-slate-600">Loading action items...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-600">
              {showCompleted
                ? "No completed items yet."
                : "No pending items. Great work!"}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {items.map((item) => (
              <Card
                key={item.id}
                className={`border-0 shadow-sm hover:shadow-md transition-shadow ${
                  item.completed ? "bg-slate-100" : "bg-white"
                }`}
              >
                {editingId === item.id ? (
                  <CardContent className="pt-6 space-y-4">
                    <Input
                      value={editDescription}
                      onChange={(e) => setEditDescription(e.target.value)}
                      placeholder="Action item description..."
                    />
                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleEdit(item.id)}
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
                  <CardContent className="pt-6 flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <Checkbox
                        checked={item.completed}
                        onCheckedChange={() => handleToggleComplete(item)}
                        className="w-6 h-6"
                      />
                      <div
                        className="flex-1 cursor-pointer"
                        onClick={() => startEdit(item)}
                      >
                        <p
                          className={`text-slate-900 ${
                            item.completed
                              ? "line-through text-slate-500"
                              : ""
                          }`}
                        >
                          {item.description}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          Created{" "}
                          {new Date(item.created_at).toLocaleDateString(
                            "en-US",
                            {
                              year: "numeric",
                              month: "short",
                              day: "numeric",
                            }
                          )}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={() => startEdit(item)}
                        variant="outline"
                        size="sm"
                      >
                        Edit
                      </Button>
                      <Button
                        onClick={() => handleDelete(item.id)}
                        variant="destructive"
                        size="sm"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
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

