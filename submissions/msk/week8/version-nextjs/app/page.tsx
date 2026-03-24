import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, SquareCheck as CheckSquare } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-slate-900 mb-4">
            Notes & Action Items
          </h1>
          <p className="text-lg text-slate-600">
            Organize your thoughts and track your tasks in one place
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-3 mb-2">
                <FileText className="w-8 h-8 text-blue-600" />
                <CardTitle className="text-2xl">Notes</CardTitle>
              </div>
              <CardDescription>
                Create and manage your notes with full text search
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="text-sm text-slate-600 space-y-2">
                <li>✓ Create notes with title and content</li>
                <li>✓ Search by title or content</li>
                <li>✓ Edit notes inline</li>
                <li>✓ Delete notes you no longer need</li>
                <li>✓ Track creation and update timestamps</li>
              </ul>
              <Link href="/notes" className="block">
                <Button className="w-full">
                  View Notes
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-3 mb-2">
                <CheckSquare className="w-8 h-8 text-green-600" />
                <CardTitle className="text-2xl">Action Items</CardTitle>
              </div>
              <CardDescription>
                Track your tasks and mark them complete as you go
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="text-sm text-slate-600 space-y-2">
                <li>✓ Create action items with descriptions</li>
                <li>✓ Toggle completion status with one click</li>
                <li>✓ Filter to show only pending or completed items</li>
                <li>✓ Edit item descriptions</li>
                <li>✓ Delete items when done</li>
              </ul>
              <Link href="/action-items" className="block">
                <Button className="w-full">
                  View Action Items
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <div className="mt-16 text-center text-sm text-slate-600">
          <p>
            Built with Next.js, React, Supabase, and shadcn/ui
          </p>
        </div>
      </div>
    </div>
  );
}

