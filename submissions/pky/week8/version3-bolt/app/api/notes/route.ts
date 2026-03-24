import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const q = searchParams.get('q') || '';
    const skip = parseInt(searchParams.get('skip') || '0');
    const limit = parseInt(searchParams.get('limit') || '20');
    const sort = searchParams.get('sort') || '-created_at';

    const descending = sort.startsWith('-');
    const field = sort.replace(/^-/, '');
    const fieldMap: Record<string, string> = {
      created_at: 'createdAt',
      updated_at: 'updatedAt',
      title: 'title',
    };
    const orderField = fieldMap[field] || 'createdAt';

    const where = q
      ? {
          OR: [
            { title: { contains: q } },
            { content: { contains: q } },
          ],
        }
      : {};

    const notes = await prisma.note.findMany({
      where,
      skip,
      take: limit,
      orderBy: { [orderField]: descending ? 'desc' : 'asc' },
    });

    return NextResponse.json(notes);
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, content } = body;

    if (!title) {
      return NextResponse.json({ error: 'title is required' }, { status: 400 });
    }

    const note = await prisma.note.create({
      data: { title, content: content || '' },
    });

    return NextResponse.json(note, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
