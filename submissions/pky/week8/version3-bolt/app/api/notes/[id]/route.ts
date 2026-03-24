import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = parseInt(params.id);
    const note = await prisma.note.findUnique({ where: { id } });

    if (!note) {
      return NextResponse.json({ error: 'Note not found' }, { status: 404 });
    }

    return NextResponse.json(note);
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = parseInt(params.id);
    const body = await request.json();

    const existing = await prisma.note.findUnique({ where: { id } });
    if (!existing) {
      return NextResponse.json({ error: 'Note not found' }, { status: 404 });
    }

    const data: Record<string, string> = {};
    if (body.title !== undefined) data.title = body.title;
    if (body.content !== undefined) data.content = body.content;

    const note = await prisma.note.update({ where: { id }, data });

    return NextResponse.json(note);
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = parseInt(params.id);
    const existing = await prisma.note.findUnique({ where: { id } });
    if (!existing) {
      return NextResponse.json({ error: 'Note not found' }, { status: 404 });
    }

    await prisma.note.delete({ where: { id } });
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
