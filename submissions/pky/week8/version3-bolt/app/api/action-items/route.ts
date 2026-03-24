import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const completed = searchParams.get('completed');
    const skip = parseInt(searchParams.get('skip') || '0');
    const limit = parseInt(searchParams.get('limit') || '20');
    const sort = searchParams.get('sort') || '-created_at';

    const descending = sort.startsWith('-');
    const field = sort.replace(/^-/, '');
    const fieldMap: Record<string, string> = {
      created_at: 'createdAt',
      updated_at: 'updatedAt',
      description: 'description',
    };
    const orderField = fieldMap[field] || 'createdAt';

    const where: Record<string, boolean> = {};
    if (completed === 'true') where.completed = true;
    if (completed === 'false') where.completed = false;

    const items = await prisma.actionItem.findMany({
      where,
      skip,
      take: limit,
      orderBy: { [orderField]: descending ? 'desc' : 'asc' },
    });

    return NextResponse.json(items);
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { description } = body;

    if (!description) {
      return NextResponse.json({ error: 'description is required' }, { status: 400 });
    }

    const item = await prisma.actionItem.create({
      data: { description },
    });

    return NextResponse.json(item, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
